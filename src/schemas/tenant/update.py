from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TenantPreferencesUpdateSchema(BaseModel):
    theme: Literal["light", "dark"] | None = None
    timezone: str | None = None
    currency: str | None = None
    enable_telegram_booking: bool | None = None
    cancel_payment_due: int | None = Field(None, ge = 0) # hours

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "theme": "dark",
            "currency": "UZS",
            "cancel_payment_due": 24
        }
    })