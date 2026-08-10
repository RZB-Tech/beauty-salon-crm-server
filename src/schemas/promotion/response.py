from datetime import datetime
from src.repository.promotion.promotion_model import PromotionType
from src.schemas.base import BaseResponseSchema
from src.schemas.promotion.create import PromotionConditionsSchema

class PromotionResponseSchema(BaseResponseSchema):
    name: str
    promo_type: PromotionType
    discount_value: int | None = None
    description: str | None = None
    start_time: datetime
    end_time: datetime
    conditions: PromotionConditionsSchema