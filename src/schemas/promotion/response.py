from datetime import datetime
from src.repository.promotion.promotion_model import PromotionType
from src.schemas.base import BaseResponseSchema

class PromotionResponseSchema(BaseResponseSchema):
    name: str
    promo_type: PromotionType
    service_id: int | None = None
    material_id: int | None = None
    discount_value: int | None = None
    description: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None