from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from src.core.utils.model_filter import apply_dynamic_filters
from src.database.base import BaseRepository
from src.repository.service.service_model import Service
from src.schemas.base import RequestAllObject
from src.schemas.service.create import ServiceCreateSchema
from src.schemas.service.update import ServiceUpdateSchema

class ServiceRepository(BaseRepository[Service]):

    async def create(self, service: ServiceCreateSchema) -> Service:
        self.db.add(service)
        await self.db.flush()
        await self.db.refresh(service)
        return service
    
    async def get_by_ids(self, ids: list[int]) -> list[Service]:
        result = await self.db.execute(
            select(Service).where(Service.id.in_(ids))
        )
        return result.scalars().all()
    
    async def get_all(self, data: RequestAllObject) -> tuple[list[Service], int]:
        count_stmt = select(func.count()).select_from(Service)
        stmt = select(Service)
        count_stmt = apply_dynamic_filters(count_stmt, Service, data.filters)
        stmt = apply_dynamic_filters(stmt, Service, data.filters)
        total_items = await self.db.scalar(count_stmt) or 0
        offset_value = (data.page - 1) * data.pageSize
        stmt = stmt.order_by(Service.id.desc()).offset(offset_value).limit(data.pageSize)
        result = await self.db.execute(stmt)
        items = result.scalars().all()
        return items, total_items