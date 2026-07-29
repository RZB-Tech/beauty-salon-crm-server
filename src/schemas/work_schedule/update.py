from typing import Annotated, Self
from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field, model_validator
from src.repository.employee.workSchedule_model import AbsenceEnum
from src.schemas.base import BaseUpdateSchema
from datetime import date, time

class WorkScheduleItemUpdateSchema(BaseModel):
    id: int = Field(ge = 1)
    start_time: time
    end_time: time

    @model_validator(mode = "after")
    def validate_request(self) -> Self:
        if self.start_time >= self.end_time: raise HTTPException(400, "Время конца должна быть строго позже начала рабочего дня")
        return self

class WorkScheduleUpdateSchema(BaseModel):
    work_schedules: Annotated[list[WorkScheduleItemUpdateSchema], Field(min_length = 1, max_length = 7)]

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "work_schedules": [
                {"id": 1, "start_time": "10:00:00", "end_time": "19:00:00"}
            ]
        }
    })

class AbsenceUpdateSchema(BaseUpdateSchema):
    id: int = Field(ge = 1)
    start_date: date | None = None
    end_date: date | None = None
    absence_type: AbsenceEnum | None = None
    reason: str | None = None
    archived: bool | None = None

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "id": 1,
            "end_date": "2026-08-16",
            "reason": "Продление отпуска"
        }
    })