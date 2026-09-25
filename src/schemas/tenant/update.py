from typing import ClassVar
from pydantic import BaseModel, ConfigDict, Field
from src.repository.staff.staff_model import StaffType
from src.schemas.base import BaseUpdateSchema


class TenantPreferencesUpdateSchema(BaseUpdateSchema):
    enable_telegram_booking: bool | None = None
    cancel_payment_due: int | None = Field(None, ge = 0) # hours
    auto_pay_subscription: bool | None = None
    time_to_confirm_booking: int | None = Field(None, ge = 1) # minutes
    booking_slot_step: int | None = Field(None, ge = 5, le = 240) # minutes

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "enable_telegram_booking": False,
            "cancel_payment_due": 24,
            "auto_pay_subscription": True
        }
    })

class UpdateBranchAdminPassword(BaseModel):
    branch_id: int = Field(ge = 1)
    admin_id: int = Field(ge = 1)
    password: str | None = Field(None, min_length = 6)

class UpdateBranchAdminSchema(BaseUpdateSchema):
    _exclude_fields: ClassVar[set[str]] = {"branch_id", "admin_id"}

    branch_id: int = Field(ge = 1)
    admin_id: int = Field(ge = 1)
    active: bool | None = None
    staff_type: StaffType | None = None

class UpdateBranchSchema(BaseUpdateSchema):
    _exclude_fields: ClassVar[set[str]] = {"branch_id"}

    branch_id: int = Field(ge = 1)
    name: str | None = Field(None, min_length = 1, max_length = 255)
    TIN: str | None = None
    active: bool | None = None

