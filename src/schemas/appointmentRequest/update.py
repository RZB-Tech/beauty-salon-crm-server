from pydantic import BaseModel, ConfigDict, Field

class AppointmentRequestConfirmSchema(BaseModel):
    id: int = Field(ge = 1)
    employee_id: int = Field(ge = 1)
    # Existing client of the organization to link the Telegram client to;
    # if omitted, the already linked client is used or a new one is created from the Telegram profile
    client_id: int | None = Field(None, ge = 1)

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "id": 1,
            "employee_id": 1
        }
    })

class AppointmentRequestDeclineSchema(BaseModel):
    id: int = Field(ge = 1)
    reason: str | None = Field(None, max_length = 1000)

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "id": 1,
            "reason": "На это время все мастера заняты"
        }
    })

class AppointmentRequestClientCancelSchema(BaseModel):
    id: int = Field(ge = 1)
