from typing import Literal

from pydantic import BaseModel, Field

class TenantPreferencesSchema(BaseModel):
    theme: Literal["light", "dark"] = "light"
    # timezone: str = "UTC"
    # currency: str = "UZS"
    enable_telegram_booking: bool = False
    cancel_payment_due: int | None = Field(1, ge = 0) # hours
