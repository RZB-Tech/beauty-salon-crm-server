from datetime import date, datetime
from pydantic import BaseModel, ConfigDict
from src.repository.client.client_model import Sex

class GlobalClientNestedResponseSchema(BaseModel):
    id: int
    telegram_user_id: int
    telegram_username: str | None = None
    telegram_phone: str
    call_phone: str | None = None
    firstname: str
    lastname: str
    middlename: str | None = None
    birth_date: date | None = None
    sex: Sex

    model_config = ConfigDict(from_attributes = True)

class GlobalClientResponseSchema(GlobalClientNestedResponseSchema):
    created_at: datetime
    updated_at: datetime
