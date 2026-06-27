from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from src.core.utils.model_filter import apply_dynamic_filters
from src.database.base import BaseRepository
from src.repository.payment.payment_model import Payment, Receipt
from src.schemas.base import RequestAllObject

class PaymentRepository(BaseRepository):
    async def create(self, receipt_id: int, payment: Payment) -> Receipt:
        stmt = (
            select(Receipt)
            .where(Receipt.id == receipt_id)
            .options(
                selectinload(Receipt.payments),
                selectinload(Receipt.appointment)
            )
        )
        result = await self.db.execute(stmt)
        receipt = result.scalar_one_or_none()

        if not receipt:
            raise ValueError(f"Receipt with id {receipt_id} not found.")

        receipt.payments.append(payment)
        self.db.add(payment)

        await self.db.flush()
        return receipt
    
    async def get(self, id: int) -> Payment | None:
        return await self.db.get(Payment, id)

    async def get_by_ids(self, ids: list[int]) -> list[Payment]:
        result = await self.db.execute(
            select(Payment).where(Payment.id.in_(ids))
        )
        return list(result.scalars().all())

    async def get_by_receipt_id(self, receipt_id: int) -> list[Payment]:
        result = await self.db.execute(
            select(Payment).where(Payment.receipt_id == receipt_id)
        )
        return list(result.scalars().all())

    async def get_all(self, data: RequestAllObject) -> tuple[list[Payment], int]:
        count_stmt = select(func.count()).select_from(Payment)
        stmt = select(Payment)

        count_stmt = apply_dynamic_filters(count_stmt, Payment, data.filters)
        stmt = apply_dynamic_filters(stmt, Payment, data.filters)

        total_items = await self.db.scalar(count_stmt) or 0

        offset_value = (data.page - 1) * data.pageSize
        stmt = stmt.order_by(Payment.id.desc()).offset(offset_value).limit(data.pageSize)

        result = await self.db.execute(stmt)
        items = list(result.scalars().all())
        return items, total_items

    # async def update(self, payload: PaymentUpdateSchema) -> Payment | None:
    #     obj = await self.db.get(Payment, payload.id)
    #     if not obj:
    #         return None

    #     update_data = payload.model_dump(exclude_unset=True)
    #     update_data.pop("id", None)

    #     for field, value in update_data.items():
    #         setattr(obj, field, value)

    #     await self.db.commit()
    #     await self.db.refresh(obj)
    #     return obj

    async def delete(self, id: int) -> bool:
        obj = await self.db.get(Payment, id)
        if not obj:
            return False

        await self.db.delete(obj)
        await self.db.commit()
        return True
    
    async def cancel(self, id: int) -> Payment | None:
        obj = await self.db.get(Payment, id)
        if not obj: return None

        await self.db.flush()
        await self.db.refresh(obj)
        return obj