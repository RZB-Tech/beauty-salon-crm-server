from datetime import datetime
from typing import Any

from sqlalchemy import func, select

from src.database.base import BaseRepository
from src.repository.employee.workSchedule_model import WorkSchedule, EmployeeAbsence
from src.schemas.base import RequestAllObject

class WorkScheduleRepository(BaseRepository[WorkSchedule]):
    async def create(self, workSchedule: WorkSchedule) -> WorkSchedule:
        self.db.add(workSchedule)
        await self.db.flush()
        await self.db.refresh(workSchedule)
        return workSchedule
    
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
        items = result.scalars().all()
        return items, total_items

    async def get_by_ids(self, ids: list[int]) -> list[WorkSchedule]:
        result = await self.db.execute(
            select(WorkSchedule)
            .where(WorkSchedule.id.in_(ids))
        )
        return result.scalars().all()
    
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