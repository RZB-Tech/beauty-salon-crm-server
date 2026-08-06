from datetime import date, time
from typing import Annotated, Self
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.repository.employee.workSchedule_model import AbsenceEnum

class WorkScheduleBaseCreateSchema(BaseModel):
    day: int = Field(ge = 1, le = 7 )
    start_time: time
    end_time: time

    @model_validator(mode = "after")
    def validate_request(self) -> Self:
        if self.start_time >= self.end_time: 
            raise ValueError("End time has to be strictly later than start time")
        return self

class WorkScheduleCreateSchema(BaseModel):
    employee_id: int = Field(ge = 1)
    work_schedules: Annotated[list[WorkScheduleBaseCreateSchema], Field(min_length = 1, max_length = 7)]

    @field_validator("work_schedules")
    @classmethod
    def validate_unique_days(cls, value: list[WorkScheduleBaseCreateSchema]) -> list[WorkScheduleBaseCreateSchema]:
        days = [schedule.day for schedule in value]
        if len(days) != len(set(days)): raise ValueError("Days has to be unique")
        return value

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "employee_id": 1,
            "work_schedules": [
                {"day": 1, "start_time": "09:00:00", "end_time": "18:00:00"},
                {"day": 2, "start_time": "09:00:00", "end_time": "18:00:00"}
            ]
        }
    })

class AbsenceCreateSchema(BaseModel):
    employee_id: int = Field(ge = 1)
    start_date: date
    end_date: date
    absence_type: AbsenceEnum
    reason: str | None = None

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "employee_id": 1,
            "start_date": "2026-08-10",
            "end_date": "2026-08-15",
            "absence_type": "vacation",
            "reason": "Ежегодный отпуск"
        }
    })