from datetime import date

from pydantic import ConfigDict, Field
from src.repository.client.client_model import Sex
from src.schemas.base import BaseResponseSchema

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
