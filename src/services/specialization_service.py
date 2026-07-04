import math
from fastapi import HTTPException
from src.core.dependencies.uow import UnitOfWork
from src.repository.employee.employee_model import Specialization
from src.schemas.base import RequestAllObject
from src.schemas.specialization.create import SpecializationCreateSchema
from src.schemas.specialization.update import SpecializationUpdateSchema

class SpecializationService():
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create(self, data: SpecializationCreateSchema) -> Specialization:
        specializationData = data.model_dump()
        newSpecialization = Specialization(**specializationData)
        return await self.uow.specializations.create(newSpecialization)
    
    async def update(self, data: SpecializationUpdateSchema) -> Specialization:
        dataDict = data.model_dump(exclude = {"id"}, exclude_unset = True)
        result = await self.uow.specializations.update(data.id, **dataDict)
        if result is None:
            raise HTTPException(
                status_code = 404,
                detail = f"Специализация с ID {data.id} не найден"
            )
        return result
    
    async def get(self, id: int) -> Specialization:
        result = await self.uow.specializations.get(id)
        if result is None:
            raise HTTPException(
                status_code = 404,
                detail = f"Специализация с ID {id} не найден"
            )
        return result
    
    async def get_many(self, ids: list[int]) -> Specialization:
        return await self.uow.specializations.get_by_ids(ids)
    
    async def get_all(self, data: RequestAllObject) -> dict:
        items, total_items = await self.uow.specializations.get_all(data)

        total_pages = math.ceil(total_items / data.pageSize) if data.pageSize > 0 else 0
        
        return {
            "items": items,
            "page": data.page,
            "pageSize": data.pageSize,
            "totalItems": total_items,
            "totalPages": total_pages
        }
    
    async def delete(self, id: int) -> bool:
        return await self.uow.specializations.delete(id)
    