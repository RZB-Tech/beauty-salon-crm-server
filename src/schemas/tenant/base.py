from typing import Literal

from pydantic import BaseModel, Field

class TenantPreferencesSchema(BaseModel):
    theme: Literal["light", "dark"] = "light"
    # timezone: str = "UTC"
    # currency: str = "UZS"
    enable_telegram_booking: bool = False
    cancel_payment_due: int | None = Field(1, ge = 0) # hours
    auto_pay_subscription: bool = False
    # Telegram booking: a pending appointment request is auto-cancelled if not confirmed within this time
    time_to_confirm_booking: int = Field(60, ge = 1) # minutes
    booking_slot_step: int = Field(30, ge = 5, le = 240) # minutes between offered start times
