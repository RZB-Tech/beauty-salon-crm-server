from datetime import date, time
from typing import Annotated, Self

from fastapi import HTTPException
from pydantic import BaseModel, Field, field_validator, model_validator

from src.repository.employee.workSchedule_model import AbsenceEnum

class WorkScheduleCreateSchema(BaseModel):
    employee_id: int = Field(ge = 1)
    days: Annotated[list[Annotated[int, Field(ge = 1, le = 7)]],
                    Field(min_length = 1, max_length = 7)]
    start_time: time
    end_time: time

    @field_validator("days")
    @classmethod
    def validate_days(cls, values: list[int]) -> list[int]:
        uniqueDays = list(set(values))
        return uniqueDays

    @model_validator(mode = "after")
    def validate_request(self) -> Self:
        if self.start_time >= self.end_time: raise HTTPException(400, "Время конца должна быть строго позже начала рабочего дня")
        return self

class AbsenceCreateSchema(BaseModel):
    employee_id: int = Field(ge = 1)
    start_date: date
    end_date: date
    absence_type: AbsenceEnum
    reason: str | None = None