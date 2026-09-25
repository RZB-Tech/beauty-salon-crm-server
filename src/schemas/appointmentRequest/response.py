from datetime import datetime
from pydantic import BaseModel, ConfigDict
from src.repository.appointment.appointment_model import AppointmentStatus
from src.repository.appointment.appointmentRequest_model import AppointmentRequestCancelledReason, AppointmentRequestStatus
from src.schemas.base import BaseResponseSchema, MoneyResponse
from src.schemas.globalClient.response import GlobalClientNestedResponseSchema

class ServiceSnapshotSchema(BaseModel):
    service_id: int | None = None
    name: str
    price: MoneyResponse
    estimated_time: int

class AppointmentRequestResponseSchema(BaseResponseSchema):
    global_client: GlobalClientNestedResponseSchema
    service_id: int | None = None
    service_snapshot: ServiceSnapshotSchema
    start_time_est: datetime
    end_time_est: datetime
    comment: str | None = None
    status: AppointmentRequestStatus
    cancelled_reason: AppointmentRequestCancelledReason | None = None
    decline_reason: str | None = None
    expires_at: datetime
    decided_at: datetime | None = None
    appointment_id: int | None = None

    model_config = ConfigDict(from_attributes = True)

class MiniAppAppointmentRequestResponseSchema(BaseModel):
    """What the client sees in the mini app: their request plus the resulting appointment's status."""
    id: int
    tenant_id: int
    tenant_name: str
    service_snapshot: ServiceSnapshotSchema
    start_time_est: datetime
    end_time_est: datetime
    comment: str | None = None
    status: AppointmentRequestStatus
    cancelled_reason: AppointmentRequestCancelledReason | None = None
    decline_reason: str | None = None
    expires_at: datetime
    decided_at: datetime | None = None
    appointment_id: int | None = None
    appointment_status: AppointmentStatus | None = None
    created_at: datetime

class MiniAppTenantResponseSchema(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes = True)

class MiniAppServiceResponseSchema(BaseModel):
    id: int
    name: str
    price: MoneyResponse
    estimated_time: int # minutes
    category_id: int | None = None

    model_config = ConfigDict(from_attributes = True)

class BookingSlotSchema(BaseModel):
    start_time_est: datetime
    end_time_est: datetime
