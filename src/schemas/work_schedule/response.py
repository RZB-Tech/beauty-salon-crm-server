from datetime import date, time
from src.repository.employee.workSchedule_model import AbsenceEnum
from src.schemas.base import BaseResponseSchema

class WorkScheduleResponseSchema(BaseResponseSchema):
    employee_id: int
    days: list[int]
    start_time: time
    end_time: time

class AbsenceResponseSchema(BaseResponseSchema):
    employee_id: int

    start_date: date
    end_date: date

    absence_type: AbsenceEnum
    reason: str | None = None