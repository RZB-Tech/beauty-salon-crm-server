from typing import Annotated

from pydantic import Field

from src.repository.employee.workSchedule_model import AbsenceEnum
from src.schemas.base import BaseUpdateSchema
from datetime import date, time

class WorkScheduleUpdateSchema(BaseUpdateSchema):
    id: int = Field(ge = 1)
    days: Annotated[list[Annotated[int, Field(ge = 1, le = 7)]],
                    Field(min_length = 1, max_length = 7)]
    start_time: time
    end_time: time

class AbsenceUpdateSchema(BaseUpdateSchema):
    id: int = Field(ge = 1)
    start_date: date | None = None
    end_date: date | None = None
    absence_type: AbsenceEnum | None = None
    reason: str | None = None
    archived: bool | None = None