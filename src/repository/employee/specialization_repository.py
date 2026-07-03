from sqlalchemy import func, select
from src.core.utils.model_filter import apply_dynamic_filters
from src.database.base import BaseRepository
from src.repository.employee.employee_model import Specialization
from src.schemas.base import RequestAllObject

class SpecializationRepository(BaseRepository[Specialization]):
    async def create(self, specialization: Specialization) -> Specialization:
        self.db.add(specialization)
        await self.db.flush()
        await self.db.refresh(specialization)
        return specialization
    
    async def get_by_ids(self, ids: list[int]) -> list[Specialization]:
        result = await self.db.execute(
            select(Specialization).where(Specialization.id.in_(ids))
        )
        return result.scalars().all()
    
    async def get_all(self, data: RequestAllObject) -> tuple[list[Specialization], int]:
        count_stmt = select(func.count()).select_from(Specialization)
        stmt = select(Specialization)
        count_stmt = apply_dynamic_filters(count_stmt, Specialization, data.filters)
        stmt = apply_dynamic_filters(stmt, Specialization, data.filters)
        total_items = await self.db.scalar(count_stmt) or 0
        offset_value = (data.page - 1) * data.pageSize
        stmt = stmt.order_by(Specialization.id.desc()).offset(offset_value).limit(data.pageSize)
        result = await self.db.execute(stmt)
        items = result.scalars().all()
        return items, total_items