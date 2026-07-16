import math
from fastapi import HTTPException, status
from src.core.decorators.requireID import require_exists
from src.core.dependencies.uow import UnitOfWork
from src.repository.employee.workSchedule_model import WorkSchedule
from src.schemas.base import RequestAllObject
from src.schemas.work_schedule.create import WorkScheduleCreateSchema
from src.schemas.work_schedule.response import WorkScheduleResponseSchema
from src.schemas.work_schedule.update import WorkScheduleUpdateSchema

class WorkScheduleService():
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    @require_exists("employees", target_param = "employee_id")
    async def create(self, data: WorkScheduleCreateSchema) -> WorkSchedule:
        workScheduleData = data.model_dump(exclude = {"days"})

        createdSchedules = [
            await self.uow.work_schedules.create(WorkSchedule(**workScheduleData, day_of_week = day))
            for day in data.days
        ]
        representative = createdSchedules[0]
        representative.days = [schedule.day_of_week for schedule in createdSchedules]
        return representative

    async def update(self, data: WorkScheduleUpdateSchema) -> WorkSchedule:
        current = await self.uow.work_schedules.get(data.id)
        if current is None:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"Рабочее время в ID {data.id} не найден"
            )

        siblings = await self.uow.work_schedules.get_group(
            current.employee_id, current.start_time, current.end_time
        )
        existingByDay = {sibling.day_of_week: sibling for sibling in siblings}
        newDays = set(data.days)

        for day, sibling in existingByDay.items():
            if day not in newDays:
                await self.uow.work_schedules.delete(sibling.id)

        updatedSchedules = []
        for day in newDays:
            sibling = existingByDay.get(day)
            if sibling is not None:
                updated = await self.uow.work_schedules.update(
                    sibling.id, start_time = data.start_time, end_time = data.end_time
                )
            else:
                updated = await self.uow.work_schedules.create(
                    WorkSchedule(
                        employee_id = current.employee_id,
                        day_of_week = day,
                        start_time = data.start_time,
                        end_time = data.end_time
                    )
                )
            updatedSchedules.append(updated)

        representative = updatedSchedules[0]
        representative.days = [schedule.day_of_week for schedule in updatedSchedules]
        return representative

    async def get(self, id: int) -> WorkSchedule:
        result = await self.uow.work_schedules.get(id)
        if result is None:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"Рабочее время в ID {id} не найден"
            )
        result.days = [result.day_of_week]
        return result

    async def get_many(self, ids: list[int]) -> list[WorkSchedule]:
        results = await self.uow.work_schedules.get_by_ids(ids)
        for result in results:
            result.days = [result.day_of_week]
        return results

    async def get_all(self, data: RequestAllObject) -> dict:
        items, total_items = await self.uow.work_schedules.get_all(data)
        for item in items:
            item.days = [item.day_of_week]

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