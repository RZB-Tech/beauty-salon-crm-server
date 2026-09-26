from typing import Self
from pydantic import BaseModel, ConfigDict, Field, model_validator
from src.schemas.appointment.create import AppointmentCreateSchema, AppointmentRecordsCreateOptionalSchema

class AppointmentRequestConfirmSchema(AppointmentCreateSchema):
    """
    The appointment staff create from the request - time, employees and services
    as they decide (pre-fill from the request's services and start time), with the
    same validation as creating an appointment by hand.

    The organization's client: `client_id` (an existing one, linked to the Telegram
    client now); otherwise the one already linked; otherwise a new one is created
    from the Telegram profile with `new_client_phone` - staff choose which of the
    client's phones (`telegram_phone` / `call_phone`) to store; defaults to
    `call_phone`, then `telegram_phone`.
    """
    id: int = Field(ge = 1)
    client_id: int | None = Field(None, ge = 1)
    new_client_phone: str | None = Field(None, min_length = 5, max_length = 50)
    records: list[AppointmentRecordsCreateOptionalSchema] = Field(min_length = 1)

    @model_validator(mode = "after")
    def client_or_new_client(self) -> Self:
        if self.client_id is not None and self.new_client_phone is not None:
            raise ValueError("Pass either client_id (existing client) or new_client_phone (new client), not both")
        return self

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "id": 1,
            "start_time_est": "2026-10-01T10:00:00Z",
            "end_time_est": "2026-10-01T11:30:00Z",
            "records": [
                {"employee_id": 1, "services": [{"service_id": 1, "quantity": 1}, {"service_id": 4, "quantity": 2}]}
            ],
            "new_client_phone": "+998901112233"
        }
    })

class AppointmentRequestDeclineSchema(BaseModel):
    id: int = Field(ge = 1)
    # Required - the client sees it
    reason: str = Field(min_length = 1, max_length = 1000)

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "id": 1,
            "reason": "На это время все мастера заняты"
        }
    })

class AppointmentRequestClientCancelSchema(BaseModel):
    id: int = Field(ge = 1)
    reason: str | None = Field(None, max_length = 1000)

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "id": 1,
            "reason": "Планы изменились"
        }
    })
