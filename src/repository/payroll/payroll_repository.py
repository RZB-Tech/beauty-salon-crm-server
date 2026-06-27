from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from src.core.utils.model_filter import apply_dynamic_filters
from src.database.base import BaseRepository
from src.repository.payroll.payroll_model import Payroll
from src.schemas.base import PaginationSchema, RequestAllObject
from src.schemas.payroll.create import PayrollCreateSchema
from src.schemas.payroll.update import PayrollUpdateSchema

class PayrollRepository(BaseRepository[Payroll]):
    async def create(self, payroll: Payroll) -> Payroll:
        self.db.add(payroll)
        await self.db.commit()
        await self.db.refresh(payroll)
        return payroll
    
    async def get_by_ids(self, ids: list[int]) -> list[Payroll]:
        result = await self.db.execute(
            select(Payroll).where(Payroll.id.in_(ids))
        )
        return list(result.scalars().all())
    
    async def get(self, id: int) -> Payroll | None:
        return await self.db.get(Payroll, id)
    
    async def get_all(self, data: RequestAllObject) -> tuple[list[Payroll], int]:
        count_stmt = select(func.count()).select_from(Payroll)
        stmt = select(Payroll)
        count_stmt = apply_dynamic_filters(count_stmt, Payroll, data.filters)
        stmt = apply_dynamic_filters(stmt, Payroll, data.filters)
        total_items = await self.db.scalar(count_stmt) or 0
        offset_value = (data.page - 1) * data.pageSize
        stmt = stmt.offset(offset_value).limit(data.pageSize)
        result = await self.db.execute(stmt)
        items = list(result.scalars().all())
        return items, total_items
    
    # async def update(self, payload: PayrollUpdateSchema) -> Payroll | None:
    #     obj = await self.db.get(Payroll, payload.id)
    #     if not obj:
    #         return None

    #     update_data = payload.model_dump(exclude_unset=True)

    #     update_data.pop("id", None)

    #     for field, value in update_data.items():
    #         setattr(obj, field, value)

    #     await self.db.commit()
    #     await self.db.refresh(obj)

    #     return obj
    
    async def get_by_employee(self, data: PaginationSchema, id: int) -> list[Payroll] | None:
        count_stmt = select(func.count()).select_from(Payroll)
        total_items = await self.db.scalar(count_stmt) or 0
        offset_value = (data.page - 1) * data.pageSize
        stmt = (
            select(Payroll)
            .where(Payroll.employee_id == id)
            .offset(offset_value)
            .limit(data.pageSize)
        )
        result = await self.db.execute(stmt)
        items = list(result.scalars().all())

        return items, total_items