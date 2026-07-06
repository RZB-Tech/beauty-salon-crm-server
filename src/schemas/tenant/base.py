from pydantic import BaseModel, Field

class TenantPreferencesSchema(BaseModel):
    theme: str = "light"
    timezone: str = "UTC"
    currency: str = "UZS"
    enable_telegram_booking: bool = False
    cancel_payment_due: int = Field(0, ge = 0) # hours