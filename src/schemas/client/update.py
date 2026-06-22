from enum import IntEnum

from src.repository.client.client_model import Sex
from src.schemas.base import BaseUpdateSchema
from pydantic import BaseModel, Field
from datetime import date

class ClientUpdateSchema(BaseUpdateSchema):
    id: int = Field(ge = 1)
    firstname: str | None = None
    lastname: str | None = None
    middlename: str | None = None
    phone: str | None = None
    birth_date: date | None = None
    sex: Sex | None = None
    notes: str | None = None

class DepositOperation(IntEnum):
    INCREMENT = 1
    DECREMENT = -1

class ClientDepositUpdateSchema(BaseModel):
    id: int = Field(ge = 1)
    operation: DepositOperation
    amount: int = Field(ge = 1)