from typing import Self

from pydantic import BaseModel, Field, field_validator, model_validator

from src.repository.transaction.transaction_model import TransactionCategory, TransactionMethod, TransactionType

NOT_ALLOWED_CATEGORIES = {
    TransactionCategory.APPOINTMENT,
    TransactionCategory.DIRECT_SALE
}

class TransactionCreateSchema(BaseModel):
    type: TransactionType
    category: TransactionCategory
    method: TransactionMethod
    amount: int = Field(ge = 1)

    notes: str | None = None

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: TransactionCategory) -> TransactionCategory:
        if value in NOT_ALLOWED_CATEGORIES:
            raise ValueError("Нельзя вручную добавлять транзакции к посещениям или продажах, для них транзакции автоматически генерируются системой после оплат")
        return value