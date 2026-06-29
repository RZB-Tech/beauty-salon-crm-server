from sqlalchemy import func, select
from src.core.utils.model_filter import apply_dynamic_filters
from src.database.base import BaseRepository
from src.repository.service.service_model import ServiceCategory
from src.schemas.service_category.create import ServiceCategoryCreateSchema
from src.schemas.service_category.update import ServiceCategoryUpdateSchema
from src.schemas.base import RequestAllObject

class ServiceCategoryRepository(BaseRepository[ServiceCategory]):
    async def create(self, serviceCategory: ServiceCategory) -> ServiceCategory:
        self.db.add(serviceCategory)
        await self.db.flush()
        await self.db.refresh(serviceCategory)
        return serviceCategory
    
    async def get(self, id: int) -> ServiceCategory:
        return await self.db.get(ServiceCategory, id)
    
    async def get_by_ids(self, ids: list[int]) -> list[ServiceCategory]:
        result = await self.db.execute(
            select(ServiceCategory).where(ServiceCategory.id.in_(ids))
        )
        return list(result.scalars().all())
    
    async def get_all(self, data: RequestAllObject) -> tuple[list[ServiceCategory], int]:
        count_stmt = select(func.count()).select_from(ServiceCategory)
        stmt = select(ServiceCategory)
        count_stmt = apply_dynamic_filters(count_stmt, ServiceCategory, data.filters)
        stmt = apply_dynamic_filters(stmt, ServiceCategory, data.filters)
        total_items = await self.db.scalar(count_stmt) or 0
        offset_value = (data.page - 1) * data.pageSize
        stmt = stmt.offset(offset_value).limit(data.pageSize)
        result = await self.db.execute(stmt)
        items = list(result.scalars().all())
        return items, total_items