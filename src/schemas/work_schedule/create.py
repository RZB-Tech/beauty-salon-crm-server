from datetime import date, time

from pydantic import BaseModel, Field

from src.repository.employee.workSchedule_model import AbsenceEnum

class WorkScheduleCreateSchema(BaseModel):
    employee_id: int = Field(ge = 1)
    day: date
    start_time: time
    end_time: time

class AbsenceCreateSchema(BaseModel):
    employee_id: int = Field(ge = 1)
    start_date: date
    end_date: date
    absence_type: AbsenceEnum
    reason: str | None = None