from datetime import date, time
from typing import Annotated, Self

from fastapi import HTTPException
from pydantic import BaseModel, Field, field_validator, model_validator

from src.repository.employee.workSchedule_model import AbsenceEnum

class WorkScheduleBaseCreateSchema(BaseModel):
    day: int = Field(ge = 1, le = 7 )
    start_time: time
    end_time: time

    @model_validator(mode = "after")
    def validate_request(self) -> Self:
        if self.start_time >= self.end_time: raise HTTPException(400, "Время конца должна быть строго позже начала рабочего дня")
        return self

class WorkScheduleCreateSchema(BaseModel):
    employee_id: int = Field(ge = 1)
    work_schedules: Annotated[list[WorkScheduleBaseCreateSchema], Field(min_length = 1, max_length = 7)]

    @field_validator("work_schedules")
    @classmethod
    def validate_unique_days(cls, value: list[WorkScheduleBaseCreateSchema]) -> list[WorkScheduleBaseCreateSchema]:
        days = [schedule.day for schedule in value]
        if len(days) != len(set(days)): raise HTTPException(400, "День не должен повторяться")
        return value

class AbsenceCreateSchema(BaseModel):
    employee_id: int = Field(ge = 1)
    start_date: date
    end_date: date
    absence_type: AbsenceEnum
    reason: str | None = None