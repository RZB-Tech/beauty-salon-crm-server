from pydantic import BaseModel
from src.schemas.base import MoneyResponse

class ReceiptAnalyticsResponse(BaseModel):
    amount: MoneyResponse
    paid: MoneyResponse
    unpaid: MoneyResponse
    cancelled: int
    average_receipt_sum: MoneyResponse
    total_paid_sum: MoneyResponse