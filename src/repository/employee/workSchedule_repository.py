from datetime import datetime
from typing import Any

from sqlalchemy import func, select

from src.database.base import BaseRepository
from src.repository.employee.workSchedule_model import WorkSchedule, EmployeeAbsence
from src.schemas.base import RequestAllObject

class WorkScheduleRepository(BaseRepository[WorkSchedule]):
    async def create(self, workSchedule: WorkSchedule) -> WorkSchedule:
        self.db.add(workSchedule)
        await self.db.commit()
        await self.db.refresh(workSchedule)
        return workSchedule

    async def get(self, id: int) -> WorkSchedule | None:
        return await self.db.get(WorkSchedule, id)
    
    async def get_all(self, data: RequestAllObject) -> tuple[list[WorkSchedule], int]:
        count_stmt = select(func.count()).select_from(WorkSchedule)
        total_items = await self.db.scalar(count_stmt) or 0
        offset_value = (data.page - 1) * data.pageSize
        stmt = (
            select(WorkSchedule)
            .offset(offset_value)
            .limit(data.pageSize)
        )
        result = await self.db.execute(stmt)
        items = list(result.scalars().all())
        return items, total_items

    async def get_by_ids(self, ids: list[int]) -> list[WorkSchedule]:
        result = await self.db.execute(
            select(WorkSchedule)
            .where(WorkSchedule.id.in_(ids))
        )
        return list(result.scalars().all())
    
    # async def update(self, data: AbsenceUpdateSchema, services: list[Service] | None = None) -> WorkSchedule | None:
    #     obj = await self.db.get(WorkSchedule, data.id)
    #     if not obj:
    #         return None

    #     update_data = data.model_dump(exclude_unset=True)
    #     update_data.pop("id", None)
    #     update_data.pop("services", None)

    #     for field, value in update_data.items():
    #         setattr(obj, field, value)

    #     if services is not None:
    #         obj.services = services 

    #     await self.db.commit()
    #     await self.db.refresh(obj)

    #     return obj
    
    async def is_employee_working(self, employee_id: int, start: datetime, end: datetime) -> bool:
        appointment_date = start.date()
        appointment_start_time = start.time()
        appointment_end_time = end.time()

        stmt = (
            select(WorkSchedule)
            .where(
                WorkSchedule.employee_id == employee_id,
                WorkSchedule.day == appointment_date,
                WorkSchedule.start_time <= appointment_start_time,
                WorkSchedule.end_time >= appointment_end_time
            )
        )
        schedule = await self.db.scalar(stmt)
        return schedule is not None
    
    async def get_workSchedules(self, id: int) -> dict[str, Any]:
        workSchedulesStmtResult = await self.db.execute(
            select(WorkSchedule)
            .where(WorkSchedule.employee_id == id)
        )
        workSchedules = workSchedulesStmtResult.scalars().all()

        absencesResult = await self.db.execute(
            select(EmployeeAbsence)
            .where(EmployeeAbsence.employee_id == id)
        )
        absences = absencesResult.scalars().all()

        return {
            "work_schedules": workSchedules,
            "absences": absences
        }