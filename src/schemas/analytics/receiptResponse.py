from pydantic import BaseModel

class ReceiptAnalyticsResponse(BaseModel):
    amount: int
    paid: int
    unpaid: int
    cancelled: int
    average_receipt_sum: float
    total_paid_sum: int