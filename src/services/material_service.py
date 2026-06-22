import math
from fastapi import HTTPException, status
from src.core.decorators.requireID import require_exists
from src.core.dependencies.uow import UnitOfWork
from src.repository.material.material_model import Material
from src.schemas.base import RequestAllObject
from src.schemas.material.create import MaterialCreateSchema
from src.schemas.material.update import MaterialOperation, MaterialQuantityUpdateSchema, MaterialUpdateSchema

class MaterialService():
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create(self, data: MaterialCreateSchema) -> Material:
        materialData = data.model_dump()
        newMaterial = Material(**materialData)
        return await self.uow.materials.create(newMaterial)

    @require_exists("materials")
    async def update(self, data: MaterialUpdateSchema) -> Material:
        return await self.uow.materials.update(data)
    
    async def get(self, id: int) -> Material:
        result = await self.uow.materials.get(id)
        if not result:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"Material with id {id} not found"
            )
        return result
    
    async def get_many(self, ids: list[int]) -> list[Material]:
        return await self.uow.materials.get_by_ids(ids)
    
    async def get_all(self, data: RequestAllObject) -> dict:
        items, total_items = await self.uow.materials.get_all(data)

        total_pages = math.ceil(total_items / data.pageSize) if data.pageSize > 0 else 0
        
        return {
            "items": items,
            "page": data.page,
            "pageSize": data.pageSize,
            "totalItems": total_items,
            "totalPages": total_pages
        }
    
    @require_exists("materials")
    async def delete(self, id: int) -> bool:
        return await self.uow.materials.delete(id)
    
    async def updateQuantity(self, data: MaterialQuantityUpdateSchema) -> Material:
        material = await self.uow.materials.get(data.id)
        if not material:
            raise HTTPException(
                status_code = status.HTTP_404_BAD_REQUEST,
                detail = f"material with id {data.id} not found"
            )
        
        if data.operation not in MaterialOperation:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Operation has to be 1 (increment) or -1 (decrement)"
            )
        
        newQuantity = material.quantity + (data.operation * data.quantity)
        if newQuantity < 0:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Quantity cannot be negative"
            )
        
        return await self.uow.materials.updateQuantity(material, newQuantity)
