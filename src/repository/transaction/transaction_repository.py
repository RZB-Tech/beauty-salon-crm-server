from datetime import timedelta

from sqlalchemy import Row, and_, func, or_, select, text
from sqlalchemy.orm import joinedload, selectinload
from src.core.utils.model_filter import apply_dynamic_filters
from src.database.base import BaseRepository
from src.repository.appointment.appointment_model import Appointment
from src.repository.receipt.receipt_model import Receipt, ReceiptItem
from src.repository.payroll.payroll_model import Payout
from src.repository.transaction.transaction_model import Transaction
from src.schemas.analytics.request import GetReportWithFilters, TranscationsByPeriod
from src.schemas.base import RequestAllObject
from src.schemas.client.request import ClientFinanceReportRequest
from src.schemas.employee.request import EmployeeFinanceReportRequest

class TransactionRepository(BaseRepository[Transaction]):
    async def create(self, transaction: Transaction) -> Transaction:
        self.db.add(transaction)
        await self.db.flush()
        await self.db.refresh(transaction)
        return transaction
    
    async def get_by_ids(self, ids: list[int]) -> list[Transaction]:
        result = await self.db.execute(
            select(Transaction).where(Transaction.id.in_(ids))
        )
        return result.scalars().all()
    
    async def get_all(self, data: RequestAllObject) -> tuple[list[Transaction], int]:
        count_stmt = select(func.count()).select_from(Transaction)
        stmt = select(Transaction)
        count_stmt = apply_dynamic_filters(count_stmt, Transaction, data.filters)
        stmt = apply_dynamic_filters(stmt, Transaction, data.filters)
        total_items = await self.db.scalar(count_stmt) or 0
        offset_value = (data.page - 1) * data.pageSize
        stmt = stmt.order_by(Transaction.id.desc()).offset(offset_value).limit(data.pageSize)
        result = await self.db.execute(stmt)
        items = result.scalars().all()
        return items, total_items

    async def get_by_receipt(self, receipt_id: int) -> list[Transaction]:
        result = await self.db.execute(
            select(Transaction).where(Transaction.receipt_id == receipt_id)
        )
        return result.scalars().all()
    
    async def get_by_client(self, data: ClientFinanceReportRequest) -> list[Transaction]:
        stmt = (
            select(Transaction)
            .join(
                Receipt,
                and_(
                    Transaction.receipt_id == Receipt.id,
                    Transaction.tenant_id == Receipt.tenant_id,
                )
            )
            .outerjoin(
                Appointment,
                and_(
                    Receipt.appointment_id == Appointment.id,
                    Receipt.tenant_id == Appointment.tenant_id,
                )
            )
            .where(
                or_(
                    Receipt.client_id == data.clientID,
                    Appointment.client_id == data.clientID,
                )
            )
            .where(Transaction.cancelled.is_(False))
            .order_by(Transaction.created_at.desc())
        )

        if data.start_date:
            stmt = stmt.where(Transaction.created_at >= data.start_date)

        if data.end_date:
            stmt = stmt.where(Transaction.created_at <= data.end_date)

        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_analytics(self, data: GetReportWithFilters) -> list[Transaction]:
        stmt = (
            select(Transaction)
            .where(and_(
                Transaction.created_at >= data.start_date,
                Transaction.created_at < data.end_date + timedelta(days = 1)
            ))
            .options(
                joinedload(Transaction.receipt)
                    .selectinload(Receipt.items)
                    .joinedload(ReceiptItem.appointment_service),
                joinedload(Transaction.receipt).selectinload(Receipt.transactions),
                joinedload(Transaction.giftCard),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_revenue_by_period(self, data: GetReportWithFilters, period: str) -> list[Row]:
        date_trunc_expr = func.date_trunc(period, Transaction.created_at)

        stmt = (
            select(
                date_trunc_expr.label("date"),
                func.sum(Transaction.amount).label("revenue"),
            )
            .where(and_(
                Transaction.created_at >= data.start_date,
                Transaction.created_at < data.end_date + timedelta(days=1)
            ))
            .group_by(date_trunc_expr)
            .order_by(date_trunc_expr)
        )

        result = await self.db.execute(stmt)
        return result.all()