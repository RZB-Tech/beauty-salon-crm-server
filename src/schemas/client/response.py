from datetime import date

from pydantic import BaseModel, ConfigDict
from src.repository.client.client_model import Sex
from src.schemas.base import BaseResponseSchema
from src.schemas.transaction.response import TransactionResponseSchema

class ClientResponseSchema(BaseResponseSchema):
    firstname: str
    lastname: str | None = None
    middlename: str | None = None
    phone: str | None = None
    birth_date: date | None = None
    sex: Sex
    deposit: int
    notes: str | None = None

    model_config = ConfigDict(from_attributes = True)

class FinanceResponseSchema(BaseModel):
    income: int
    expense: int
    net: int
    transactions: list[TransactionResponseSchema] = []

class ClientFinanceResponseSchema(BaseModel):
    items: dict[date, FinanceResponseSchema]