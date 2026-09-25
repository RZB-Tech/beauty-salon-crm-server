from datetime import datetime

from pydantic import BaseModel, ConfigDict
from src.schemas.base import MoneyResponse

class ClickCheckoutResponseSchema(BaseModel):
    transaction_id: int
    checkout_url: str
    amount: MoneyResponse

class ClickPaymentStatusSchema(BaseModel):
    id: int
    amount: MoneyResponse
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes = True)
