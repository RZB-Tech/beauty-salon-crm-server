from datetime import date
from pydantic import BaseModel, ConfigDict, Field
from src.repository.client.client_model import Sex

class GlobalClientContactSchema(BaseModel):
    # Raw `response` string from WebApp.requestContact's callback - signed by Telegram like initData
    response: str = Field(min_length = 1)

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "response": "contact=%7B%22user_id%22%3A123456789%2C%22phone_number%22%3A%22998901112233%22%2C%22first_name%22%3A%22Anna%22%7D&auth_date=1758800000&hash=..."
        }
    })

class GlobalClientRegisterSchema(BaseModel):
    firstname: str = Field(min_length = 1, max_length = 255)
    lastname: str = Field(min_length = 1, max_length = 255)
    middlename: str | None = Field(None, max_length = 255)
    birth_date: date | None = None
    sex: Sex
    # Optional number to call, if it differs from the Telegram one
    call_phone: str | None = Field(None, min_length = 5, max_length = 50)
    # Raw `response` string from WebApp.requestContact - the verified Telegram phone
    contact: str = Field(min_length = 1)

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "firstname": "Анна",
            "lastname": "Смирнова",
            "sex": "female",
            "call_phone": "+998901112233",
            "contact": "contact=%7B%22user_id%22%3A123456789%2C%22phone_number%22%3A%22998901112233%22%7D&auth_date=1758800000&hash=..."
        }
    })
