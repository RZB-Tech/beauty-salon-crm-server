from datetime import timedelta

from sqlalchemy import Numeric, Row, and_, case, cast, func, select
from sqlalchemy.orm import selectinload
from src.core.utils.model_filter import apply_dynamic_filters
from src.database.base import BaseRepository
from src.repository.receipt.receipt_model import Receipt, ReceiptStatus
from src.repository.transaction.transaction_model import Transaction
from src.schemas.analytics.request import GetReportWithFilters
from src.schemas.base import RequestAllObject

class ReceiptRepository(BaseRepository[Receipt]):
    async def create(self, receipt: Receipt) -> Receipt | None:
        self.db.add(receipt)
        await self.db.flush()
        await self.db.refresh(receipt)

        stmt = (
            select(Receipt)
            .where(Receipt.id == receipt.id)
            .options(
                selectinload(Receipt.items),
                selectinload(Receipt.transactions)
            )
        )

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get(self, id: int) -> Receipt | None:
        result = await self.db.execute(
            select(Receipt)
            .where(Receipt.id == id)
            .options(
                selectinload(Receipt.items),
                selectinload(Receipt.transactions),
                selectinload(Receipt.appointment)
            )
            .execution_options(populate_existing=True)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, data: RequestAllObject) -> tuple[list[Receipt], int]:
        count_stmt = select(func.count()).select_from(Receipt)
        stmt = select(Receipt)
        count_stmt = apply_dynamic_filters(count_stmt, Receipt, data.filters)
        stmt = apply_dynamic_filters(stmt, Receipt, data.filters)
        total_items = await self.db.scalar(count_stmt) or 0
        offset_value = (data.page - 1) * data.pageSize
        stmt = (stmt
                .options(
                    selectinload(Receipt.items),
                    selectinload(Receipt.transactions))
                .order_by(Receipt.id.desc())
                .offset(offset_value)
                .limit(data.pageSize))
        result = await self.db.execute(stmt)
        items = result.scalars().all()
        return items, total_items
    
    async def get_by_appointment(self, appointmentID: int, active: bool = False) -> list[Receipt]:
        conditions = [Receipt.appointment_id == appointmentID]
        if active: conditions.append(Receipt.status != ReceiptStatus.CANCELLED)

        stmt = (
            select(Receipt)
            .where(*conditions)
            .order_by(Receipt.id.desc())
            .options(selectinload(Receipt.items),
                     selectinload(Receipt.transactions)))
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_analytics(self, data: GetReportWithFilters) -> Row:
        paid_amount_subq = (
            select(func.coalesce(func.sum(Transaction.amount), 0))
            .where(and_(
                Transaction.receipt_id == Receipt.id,
                Transaction.tenant_id == data.branch_id
            ))
            .correlate(Receipt)
            .scalar_subquery()
        )

        # Equivalent of the WITH totals AS (...) block
        totals = (
            select(
                func.count(Receipt.id).label("amount"),
                func.sum(case((Receipt.status == ReceiptStatus.PAID, 1), else_=0)).label("paid"),
                func.sum(case((Receipt.status == ReceiptStatus.PENDING, 1), else_=0)).label("unpaid"),
                func.sum(case((Receipt.status == ReceiptStatus.CANCELLED, 1), else_=0)).label("cancelled"),
                func.coalesce(func.sum(paid_amount_subq), 0).label("total_paid_sum"),
            )
            .where(and_(
                Receipt.created_at >= data.start_date,
                Receipt.created_at < data.end_date + timedelta(days=1),
                Receipt.tenant_id == data.branch_id
            ))
            .cte("totals")
        )

        # Outer SELECT referencing the CTE
        stmt = select(
            totals.c.amount,
            totals.c.paid,
            totals.c.unpaid,
            totals.c.cancelled,
            totals.c.total_paid_sum,
            func.round(
                cast(totals.c.total_paid_sum, Numeric) / func.nullif(totals.c.amount, 0),
                2
            ).label("average"),
        ).execution_options(skip_tenant_filter = True)

        result = await self.db.execute(stmt)
        return result.one()