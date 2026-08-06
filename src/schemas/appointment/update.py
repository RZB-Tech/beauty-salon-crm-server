from typing import Self
from src.repository.appointment.appointment_model import AppointmentCancelledReason, AppointmentStatus
from src.schemas.base import BaseUpdateSchema
from pydantic import ConfigDict, Field, model_validator

class AppointmentUpdateSchema(BaseUpdateSchema):
    id: int = Field(ge = 1)
    status: AppointmentStatus | None = None
    notes: str | None = None
    archived: bool | None = None

    @model_validator(mode = "after")
    def check_status(self) -> Self:
        if self.status and self.status not in [AppointmentStatus.AWAITING, AppointmentStatus.STARTED, AppointmentStatus.FINISHED]:
            raise ValueError("Status has to be among Awaiting / Started / Finished")
        return self

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "id": 1,
            "status": "started"
        }
    })

class AppointmentServiceUpdateSchema(BaseUpdateSchema):
    id: int = Field(ge = 1)
    service_id: int | None = Field(None, ge = 1)
    material_id: int | None = Field(None, ge = 1)
    quantity: int | None = Field(None, ge = 1)
    price: int | None = Field(None, ge = 1)
    price_changed_reason: str | None = Field(None, min_length = 5)
    notes: str | None = None
    archived: bool | None = None

    @model_validator(mode = "after")
    def check_require_one_field(self) -> Self:
        if self.service_id is not None and self.material_id is not None:
            raise ValueError("Either Service or Material can be provided, not both of them.")

        return self

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "id": 1,
            "quantity": 2
        }
    })

class AppointmentCancelSchema(BaseUpdateSchema):
    id: int = Field(ge = 1)
    reason: AppointmentCancelledReason = AppointmentCancelledReason.MISTAKEN_INPUT

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "id": 1,
            "reason": "client changed his mind"
        }
    })