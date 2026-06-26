from typing import Self

from pydantic import BaseModel, Field, model_validator

from src.repository.transaction.transaction_model import TransactionCategory, TransactionMethod, TransactionType

class TransactionCreateSchema(BaseModel):
    type: TransactionType
    category: TransactionCategory
    method: TransactionMethod
    amount: int = Field(ge = 1)

    notes: str | None = None