from typing import Literal

from pydantic import  Field
from src.schemas.base import BaseUpdateSchema

class TranscationPreferencesUpdateSchema(BaseUpdateSchema):
    theme: Literal["light", "dark"] | None = None
    timezone: str = "UTC"
    currency: str = "UZS"
    enable_telegram_booking: bool = False
    cancel_payment_due: int = Field(0, ge = 0) # hours