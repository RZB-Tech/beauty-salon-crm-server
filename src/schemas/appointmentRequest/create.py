from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, Field, field_validator

class AppointmentRequestServiceSchema(BaseModel):
    service_id: int = Field(ge = 1)
    quantity: int = Field(1, ge = 1, le = 20)

class AppointmentRequestCreateSchema(BaseModel):
    tenant_id: int = Field(ge = 1)
    services: list[AppointmentRequestServiceSchema] = Field(min_length = 1, max_length = 20)
    # Any future time the client wants - no schedules are checked; staff decide on confirm.
    # The end time is estimated from the services' durations x quantity.
    start_time_est: datetime
    comment: str | None = Field(None, max_length = 1000)

    @field_validator("services", mode = "after")
    @classmethod
    def unique_services(cls, v: list[AppointmentRequestServiceSchema]) -> list[AppointmentRequestServiceSchema]:
        ids = [s.service_id for s in v]
        if len(ids) != len(set(ids)): raise ValueError("Each service can appear once - use quantity instead")
        return v

    @field_validator("start_time_est", mode = "after")
    @classmethod
    def to_utc_minutes(cls, v: datetime) -> datetime:
        if v.tzinfo is None: v = v.replace(tzinfo = timezone.utc)
        return v.astimezone(timezone.utc).replace(second = 0, microsecond = 0)

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "tenant_id": 1,
            "services": [{"service_id": 1, "quantity": 1}, {"service_id": 4, "quantity": 2}],
            "start_time_est": "2026-10-01T10:00:00Z",
            "comment": "Хочу к мастеру Анне, если можно"
        }
    })
