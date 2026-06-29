from pydantic import Field

from src.repository.employee.workSchedule_model import AbsenceEnum
from src.schemas.base import BaseUpdateSchema
from datetime import date, time

class WorkScheduleUpdateSchema(BaseUpdateSchema):
    id: int = Field(ge = 1)
    day: date | None = None
    start_time: time | None = None
    end_time: time | None = None
    archived: bool | None = None

class AbsenceUpdateSchema(BaseUpdateSchema):
    id: int = Field(ge = 1)
    start_date: date | None = None
    end_date: date | None = None
    absence_type: AbsenceEnum | None = None
    reason: str | None = None
    archived: bool | None = None