from pydantic import  Field, field_validator
from src.repository.transaction.transaction_model import TransactionCategory, TransactionMethod
from src.schemas.base import BaseUpdateSchema
from src.schemas.transaction.create import NOT_ALLOWED_CATEGORIES

class TransactionUpdateSchema(BaseUpdateSchema):
    id: int
    amount: int | None = Field(None, ge = 1)
    method: TransactionMethod | None = None
    category: TransactionCategory | None = None
    notes: str | None = None
    archived: bool | None = None

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: TransactionCategory) -> TransactionCategory:
        if value in NOT_ALLOWED_CATEGORIES:
            raise ValueError("Restricted to manually create transaction for receipts and employee's payouts")
        return value