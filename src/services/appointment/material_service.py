import math
from fastapi import HTTPException, status
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

    async def update(self, data: MaterialUpdateSchema) -> Material:
        dataDict = data.model_dump(exclude={"id"}, exclude_unset=True)
        
        for key in ["article", "name"]:
            if key in dataDict and not dataDict[key]:
                raise HTTPException(400, f"{key} не может быть пустым")

        result = await self.uow.materials.update(data.id, **dataDict)
        if result is None:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"Товар с ID {data.id} не найден"
            )
        return result
    
    async def get(self, id: int) -> Material:
        result = await self.uow.materials.get(id)
        if result is None:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"Товар с ID {id} не найден"
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

    async def delete(self, id: int) -> bool:
        return await self.uow.materials.delete(id)
    
    async def updateQuantity(self, data: MaterialQuantityUpdateSchema) -> Material:
        material = await self.uow.materials.get(data.id)
        if material is None:
            raise HTTPException(
                status_code = status.HTTP_404_BAD_REQUEST,
                detail = f"Материал с ID {data.id} не найден"
            )
        
        if data.operation not in MaterialOperation:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Операция должна быть 1 (прибавить) или -1 (убавить)"
            )
        
        newQuantity = material.quantity + (data.operation * data.quantity)
        if newQuantity < 0:
            raise HTTPException(
                status_code = 409,
                detail = "Количество материала не может быть негативным"
            )
        
        return await self.uow.materials.update(material.id, quantity = newQuantity)
