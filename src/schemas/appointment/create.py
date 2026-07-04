from typing import Self

from fastapi import HTTPException
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime

class AppointmentServicesCreateSchema(BaseModel):
    appointment_record_id: int = Field(ge = 1)
    service_id: int | None = Field(default = None, ge = 1)
    material_id: int | None = Field(default = None, ge = 1)
    quantity: int = Field(default = 1, ge = 1)
    price: int | None = Field(None, ge = 1)
    price_changed_reason: str | None = Field(None, min_length = 5)
    notes: str | None = None

    @model_validator(mode = "after")
    def check_service_or_material(self) -> Self:
        if self.service_id is None and self.material_id is None:
            raise HTTPException(400, "Необходимо указать либо Услугу либо Товар")

        if self.service_id is not None and self.material_id is not None:
            raise HTTPException(400, "В одном запросе можно указывать либо Услугу либо Товар")
        
        return self

class AppointmentServicesCreateOptionalSchema(AppointmentServicesCreateSchema):
    appointment_record_id: None = None

class AppointmentRecordsCreateSchema(BaseModel):
    appointment_id: int = Field(ge = 1)
    employee_id: int = Field(ge = 1)
    services: list[AppointmentServicesCreateOptionalSchema]

class AppointmentRecordsCreateOptionalSchema(AppointmentRecordsCreateSchema):
    appointment_id: None = None
    services: list[AppointmentServicesCreateOptionalSchema]
    
class AppointmentCreateSchema(BaseModel):
    client_id: int = Field(ge = 1)
    start_time_est: datetime
    end_time_est: datetime
    records: list[AppointmentRecordsCreateOptionalSchema] | None = None
    notes: str | None = None

    @field_validator("start_time_est", "end_time_est", mode = "before")
    @classmethod
    def truncate_milliseconds(cls, v):
        if isinstance(v, str):
            v = datetime.fromisoformat(v.replace("Z", "+00:00"))
        if isinstance(v, datetime):
            return v.replace(microsecond = 0)
        return v
    
    @model_validator(mode="after")
    def validate_time_range(self) -> AppointmentCreateSchema:
        if self.start_time_est >= self.end_time_est:
            raise ValueError("end_time_est must be strictly after start_time_est")
        return self