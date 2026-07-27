from datetime import date, time
from pydantic import BaseModel
from src.repository.employee.workSchedule_model import AbsenceEnum
from src.schemas.base import BaseResponseSchema

class WorkScheduleBaseResponseSchema(BaseResponseSchema):
    day: int
    start_time: time
    end_time: time

class WorkScheduleResponseSchema(BaseModel):
    employee_id: int
    work_schedules: list[WorkScheduleBaseResponseSchema]

class AbsenceResponseSchema(BaseResponseSchema):
    employee_id: int

    start_date: date
    end_date: date

    absence_type: AbsenceEnum
    reason: str | None = None