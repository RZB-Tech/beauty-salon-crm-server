from datetime import date

from sqlalchemy import and_, func, or_, select
from src.core.utils.model_filter import apply_dynamic_filters
from src.database.base import BaseRepository
from src.repository.appointment.appointment_model import Appointment
from src.repository.payment.payment_model import Receipt
from src.repository.transaction.transaction_model import Transaction
from src.schemas.base import RequestAllObject
from src.schemas.client.request import FinanceReportRequest

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

    async def get_by_client(self, data: FinanceReportRequest) -> list[Transaction]:
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