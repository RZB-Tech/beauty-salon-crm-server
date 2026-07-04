from typing import Self

from src.repository.appointment.appointment_model import AppointmentStatus
from src.schemas.base import BaseUpdateSchema
from pydantic import  Field, model_validator

class AppointmentUpdateSchema(BaseUpdateSchema):
    id: int = Field(ge = 1)
    status: AppointmentStatus | None = None
    notes: str | None = None

    @model_validator(mode = "after")
    def check_status(self) -> Self:
        if self.status and self.status not in [AppointmentStatus.AWAITING, AppointmentStatus.STARTED, AppointmentStatus.FINISHED]:
            raise ValueError("Статус должен быть Ожидается / Начат / Завершен")
        return self