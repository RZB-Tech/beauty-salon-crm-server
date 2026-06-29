from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from src.core.utils.model_filter import apply_dynamic_filters
from src.database.base import BaseRepository
from src.repository.appointment.appointment_model import Appointment, AppointmentRecords
from src.repository.payment.payment_model import Receipt, ReceiptItem, ReceiptStatus
from src.schemas.base import RequestAllObject
from src.schemas.payment.create import ReceiptCreateSchema

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
                selectinload(Receipt.payments)
            )
        )

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get(self, id: int) -> Receipt:
        result = await self.db.execute(
            select(Receipt)
            .where(Receipt.id == id)
            .options(
                selectinload(Receipt.items),
                selectinload(Receipt.payments),
                selectinload(Receipt.appointment)
            )
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
                    selectinload(Receipt.payments))
                .order_by(Receipt.id.desc())
                .offset(offset_value)
                .limit(data.pageSize))
        result = await self.db.execute(stmt)
        items = list(result.scalars().all())
        return items, total_items