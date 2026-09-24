from pydantic import BaseModel
from src.schemas.base import MoneyResponse

class ClickCheckoutResponseSchema(BaseModel):
    transaction_id: int
    checkout_url: str
    amount: MoneyResponse
