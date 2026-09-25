from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, Field, field_validator

class AppointmentRequestCreateSchema(BaseModel):
    tenant_id: int = Field(ge = 1)
    service_id: int = Field(ge = 1)
    # End time is derived from the service's estimated_time
    start_time_est: datetime
    comment: str | None = Field(None, max_length = 1000)

    @field_validator("start_time_est", mode = "after")
    @classmethod
    def to_utc_minutes(cls, v: datetime) -> datetime:
        if v.tzinfo is None: v = v.replace(tzinfo = timezone.utc)
        return v.astimezone(timezone.utc).replace(second = 0, microsecond = 0)

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "tenant_id": 1,
            "service_id": 1,
            "start_time_est": "2026-10-01T10:00:00Z",
            "comment": "Хочу к мастеру Анне, если можно"
        }
    })
