from datetime import date
from pydantic import BaseModel, ConfigDict
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

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "firstname": "Анна",
            "lastname": "Смирнова",
            "middlename": None,
            "phone": "+998901112233",
            "birth_date": "1998-03-15",
            "sex": "female",
            "deposit": 0,
            "notes": "Постоянный клиент"
        }
    })