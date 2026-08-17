from src.repository.giftCard.giftCard_model import GiftCardStatus
from src.schemas.base import BaseUpdateSchema
from pydantic import Field
from datetime import datetime

class GiftCardUpdateSchema(BaseUpdateSchema):
    id: int = Field(ge = 1)
    expiration_date: datetime | None = None
    archived: bool | None = None