import math
from fastapi import HTTPException, status
from src.core.decorators.requireID import require_exists
from src.core.dependencies.uow import UnitOfWork
from src.repository.employee.workSchedule_model import WorkSchedule
from src.schemas.base import RequestAllObject
from src.schemas.work_schedule.create import WorkScheduleCreateSchema
from src.schemas.work_schedule.update import WorkScheduleUpdateSchema

class WorkScheduleService():
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    @require_exists("employees", target_param = "employee_id")
    async def create(self, data: WorkScheduleCreateSchema) -> WorkSchedule:
        workScheduleData = data.model_dump()
        newObject = WorkSchedule(**workScheduleData)
        return await self.uow.work_schedules.create(newObject)

    async def update(self, data: WorkScheduleUpdateSchema) -> WorkSchedule:
        dataDict = data.model_dump(exclude={"id"}, exclude_unset=True)
        result = await self.uow.work_schedules.update(data.id, **dataDict)
        if result is None:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"Рабочее время в ID {data.id} не найден"
            )
        return result
    
    async def get(self, id: int) -> WorkSchedule:
        result = await self.uow.work_schedules.get(id)
        if result is None:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"Рабочее время в ID {id} не найден"
            )
        return result
    
    async def get_many(self, ids: list[int]) -> list[WorkSchedule]:
        return await self.uow.work_schedules.get_by_ids(ids)
    
    async def get_all(self, data: RequestAllObject) -> dict:
        items, total_items = await self.uow.work_schedules.get_all(data)

        total_pages = math.ceil(total_items / data.pageSize) if data.pageSize > 0 else 0
        
        return {
            "items": items,
            "page": data.page,
            "pageSize": data.pageSize,
            "totalItems": total_items,
            "totalPages": total_pages
        }
    
    async def delete(self, id: int) -> bool:
        result = await self.uow.work_schedules.delete(id)
        if result is None:
            raise HTTPException(404, f"Рабочее время с ID {id} не найден")
        return result