import math
from fastapi import HTTPException, status
from src.core.decorators.requireID import require_exists
from src.core.dependencies.uow import UnitOfWork
from src.repository.service.serviceCategory_repository import ServiceCategoryRepository
from src.repository.service.service_model import ServiceCategory
from src.schemas.service_category.create import ServiceCategoryCreateSchema
from src.schemas.service_category.update import ServiceCategoryUpdateSchema
from src.schemas.base import RequestAllObject

class ServiceCategoryService():
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create(self, data: ServiceCategoryCreateSchema) -> ServiceCategory:
        serviceData = data.model_dump()
        newServiceCategory = ServiceCategory(**serviceData)
        return await self.uow.serviceCategory.create(newServiceCategory)
    
    @require_exists("serviceCategory")
    async def update(self, data: ServiceCategoryUpdateSchema) -> ServiceCategory:
        return await self.uow.serviceCategory.update(data)
    
    async def get(self, id: int) -> ServiceCategory:
        result = await self.uow.serviceCategory.get(id)
        if not result:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"Service category with id {id} not found"
            )
        return result
    
    async def get_many(self, ids: list[int]) -> ServiceCategory:
        return await self.uow.serviceCategory.get_by_ids(ids)
    
    async def get_all(self, data: RequestAllObject) -> dict:
        items, total_items = await self.uow.serviceCategory.get_all(data)

        total_pages = math.ceil(total_items / data.pageSize) if data.pageSize > 0 else 0
        
        return {
            "items": items,
            "page": data.page,
            "pageSize": data.pageSize,
            "totalItems": total_items,
            "totalPages": total_pages
        }
    
    async def archive(self, id: int) -> ServiceCategory:
        return await self.uow.serviceCategory.archive(id)

    async def delete(self, id: int) -> bool:
        return await self.uow.serviceCategory.delete(id)
    