from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from src.core.utils.model_filter import apply_dynamic_filters
from src.database.base import BaseRepository
from src.repository.payroll.payroll_model import Payout, PayoutStatus
from src.schemas.base import PaginationSchema, RequestAllObject

class PayoutRepository(BaseRepository):
    async def create(self, payout: Payout) -> Payout:
        self.db.add(payout)
        await self.db.commit()
        await self.db.refresh(payout)
        return payout
    
    async def get_by_ids(self, ids: list[int]) -> list[Payout]:
        result = await self.db.execute(
            select(Payout).where(Payout.id.in_(ids))
        )
        return list(result.scalars().all())
    
    async def get(self, id: int) -> Payout | None:
        return await self.db.get(Payout, id)
    
    async def get_all(self, data: RequestAllObject) -> tuple[list[Payout], int]:
        count_stmt = select(func.count()).select_from(Payout)
        stmt = select(Payout)
        count_stmt = apply_dynamic_filters(count_stmt, Payout, data.filters)
        stmt = apply_dynamic_filters(stmt, Payout, data.filters)
        total_items = await self.db.scalar(count_stmt) or 0
        offset_value = (data.page - 1) * data.pageSize
        stmt = stmt.offset(offset_value).limit(data.pageSize)
        result = await self.db.execute(stmt)
        items = list(result.scalars().all())
        return items, total_items
    
    async def changeStatus(self, id: int, status: PayoutStatus) -> Payout | None:
        obj = await self.db.get(Payout, id)
        if not obj: return None

        obj.status = status
        await self.flush()
        await self.refresh(obj)
        return obj
    
    # async def update(self, payload: PayrollUpdateSchema) -> Payout | None:
    #     obj = await self.db.get(Payout, payload.id)
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
        obj = await self.db.get(Payout, id)
        if not obj:
            return False

        await self.db.delete(obj)
        await self.db.commit()
        return True
    
    async def get_by_employee(self, data: PaginationSchema, id: int) -> list[Payout] | None:
        count_stmt = (select(func.count())
            .select_from(Payout)
            .where(Payout.employee_id == id))
        total_items = await self.db.scalar(count_stmt) or 0
        offset_value = (data.page - 1) * data.pageSize
        stmt = (
            select(Payout)
            .where(Payout.employee_id == id)
            .offset(offset_value)
            .limit(data.pageSize)
        )
        result = await self.db.execute(stmt)
        items = list(result.scalars().all())

        return items, total_items