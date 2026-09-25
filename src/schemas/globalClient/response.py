from datetime import date, datetime
from pydantic import BaseModel, ConfigDict
from src.repository.client.client_model import Sex

class GlobalClientNestedResponseSchema(BaseModel):
    id: int
    telegram_username: str | None = None
    contact_phone: str | None = None
    call_phone: str | None = None
    firstname: str
    lastname: str | None = None
    middlename: str | None = None
    birth_date: date | None = None
    sex: Sex | None = None

    model_config = ConfigDict(from_attributes = True)

class GlobalClientResponseSchema(GlobalClientNestedResponseSchema):
    telegram_user_id: int
    is_profile_complete: bool
    created_at: datetime
    updated_at: datetime
