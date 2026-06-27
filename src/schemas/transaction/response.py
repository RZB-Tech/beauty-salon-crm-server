from src.repository.transaction.transaction_model import TransactionCategory, TransactionMethod, TransactionType
from src.schemas.base import BaseResponseSchema

class TransactionResponseSchema(BaseResponseSchema):
    amount: int
    type: TransactionType
    method: TransactionMethod
    category: TransactionCategory
    
    receipt_id: int | None
    payout_id: int | None

    notes: str | None
    auto_generated: bool