from datetime import datetime
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.repository.transaction.transaction_model import TransactionMethod

class GiftCardCreateSchema(BaseModel):
    client_id: int | None = Field(None, ge = 1)
    initial_amount: int = Field(ge = 1)
    issue_date: datetime
    expiration_date: datetime | None = None
    payment_method: TransactionMethod

    @model_validator(mode = "after")
    def validate_model(self) -> Self:
        if self.expiration_date is not None and self.issue_date >= self.expiration_date:
            raise ValueError("`issue_date` has to be earlier than `expiration_date`")
        return self

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "client_id": 1,
            "initial_amount": 500000,
            "expiration_date": "2026-10-10T00:00:00Z",
            "payment_method": TransactionMethod.CASH
        }
    })