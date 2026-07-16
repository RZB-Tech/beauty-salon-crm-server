from datetime import datetime, time
from typing import Any

from sqlalchemy import and_, func, select

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
            .order_by(WorkSchedule.id.desc())
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

    async def get_group(self, employee_id: int, start_time: time, end_time: time) -> list[WorkSchedule]:
        result = await self.db.execute(
            select(WorkSchedule)
            .where(
                WorkSchedule.employee_id == employee_id,
                WorkSchedule.start_time == start_time,
                WorkSchedule.end_time == end_time
            )
        )
        return list(result.scalars().all())

    async def is_employee_working(
        self, 
        employee_id: int,
        start: datetime, 
        end: datetime
    ) -> bool:
        appointment_date = start.date()
        appointment_start_time = start.time()
        appointment_end_time = end.time()
        day_of_week = appointment_date.isoweekday()

        if start.date() != end.date():
            return False 

        stmt = (
            select(WorkSchedule)
            .outerjoin(
                EmployeeAbsence,
                and_(
                    EmployeeAbsence.employee_id == WorkSchedule.employee_id,
                    EmployeeAbsence.start_date <= appointment_date,
                    EmployeeAbsence.end_date >= appointment_date
                )
            )
            .where(
                WorkSchedule.employee_id == employee_id,
                WorkSchedule.day_of_week == day_of_week,
                WorkSchedule.start_time <= appointment_start_time,
                WorkSchedule.end_time >= appointment_end_time,
                EmployeeAbsence.id.is_(None)
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
        for workSchedule in workSchedules:
            workSchedule.days = [workSchedule.day_of_week]

        absencesResult = await self.db.execute(
            select(EmployeeAbsence)
            .where(EmployeeAbsence.employee_id == id)
        )
        absences = absencesResult.scalars().all()

        return {
            "work_schedules": workSchedules,
            "absences": absences
        }