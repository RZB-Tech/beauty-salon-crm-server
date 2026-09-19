from datetime import datetime
from src.repository.giftCard.giftCard_model import GiftCardStatus
from src.schemas.base import BaseResponseSchema, MoneyResponse

class GiftCardResponseSchema(BaseResponseSchema):
    code: str
    client_id: int | None = None
    receipt_id: int
    initial_amount: MoneyResponse
    remain_amount: MoneyResponse
    status: GiftCardStatus
    issue_date: datetime
    expiration_date: datetime | None = None