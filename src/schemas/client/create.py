from datetime import date
from pydantic import BaseModel
from src.repository.client.client_model import Sex

class ClientCreateSchema(BaseModel):
    firstname: str
    lastname: str | None = None
    middlename: str | None = None
    phone: str | None = None
    birth_date: date | None = None
    sex: Sex
    deposit: int = 0
    notes: str | None = None