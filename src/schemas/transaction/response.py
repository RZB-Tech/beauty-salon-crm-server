from src.repository.transaction.transaction_model import TransactionCategory, TransactionMethod, TransactionType
from src.schemas.base import BaseResponseSchema, MoneyResponse

class TransactionResponseSchema(BaseResponseSchema):
    amount: MoneyResponse
    type: TransactionType
    method: TransactionMethod
    category: TransactionCategory
    
    receipt_id: int | None
    payout_id: int | None
    cancelled: bool

    notes: str | None
    auto_generated: bool