from pydantic import ConfigDict
from datetime import datetime
from src.repository.appointment.appointment_model import AppointmentStatus
from src.schemas.base import BaseResponseSchema

class ClientNestedResponseSchema(BaseResponseSchema):
    firstname: str
    lastname: str | None = None
    phone: str | None = None

    model_config = ConfigDict(from_attributes=True)

class EmployeeNestedResponseSchema(BaseResponseSchema):
    firstname: str
    lastname: str | None = None

    model_config = ConfigDict(from_attributes=True)

class ServiceNestedResponseSchema(BaseResponseSchema):
    name: str

    model_config = ConfigDict(from_attributes=True)

class AppointmentServicesResponseSchema(BaseResponseSchema):
    appointment_record_id: int
    service_id: int
    service: ServiceNestedResponseSchema | None = None
    material_id: int | None = None
    quantity: int
    price: int
    price_changed_reason: str | None = None
    notes: str | None = None

class AppointmentRecordsResponseSchema(BaseResponseSchema):
    appointment_id: int
    employee_id: int
    employee: EmployeeNestedResponseSchema | None = None
    services: list[AppointmentServicesResponseSchema]

class AppointmentResponseSchema(BaseResponseSchema):
    client: ClientNestedResponseSchema
    start_time_est: datetime
    end_time_est: datetime
    status: AppointmentStatus
    paid: bool = False
    total_price: int = 0
    records: list[AppointmentRecordsResponseSchema] | None = None
    notes: str | None = None