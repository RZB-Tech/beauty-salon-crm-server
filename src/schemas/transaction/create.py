from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.repository.transaction.transaction_model import TransactionCategory, TransactionMethod, TransactionType

NOT_ALLOWED_CATEGORIES = {
    TransactionCategory.RECEIPT,
    TransactionCategory.EMPLOYEE_PAYMENT
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

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "type": "expense",
            "category": "utility",
            "method": "card",
            "amount": 250000,
            "notes": "Оплата коммунальных услуг за июль"
        }
    })