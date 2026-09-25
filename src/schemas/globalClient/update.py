from datetime import date
from pydantic import ConfigDict, Field
from src.repository.client.client_model import Sex
from src.schemas.base import BaseUpdateSchema

class GlobalClientUpdateSchema(BaseUpdateSchema):
    firstname: str | None = Field(None, min_length = 1, max_length = 255)
    lastname: str | None = Field(None, max_length = 255)
    middlename: str | None = Field(None, max_length = 255)
    birth_date: date | None = None
    sex: Sex | None = None
    call_phone: str | None = Field(None, min_length = 5, max_length = 50)

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "firstname": "Анна",
            "lastname": "Смирнова",
            "birth_date": "1998-03-15",
            "sex": "female",
            "call_phone": "+998901112233"
        }
    })
