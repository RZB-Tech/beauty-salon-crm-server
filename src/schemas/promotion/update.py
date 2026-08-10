from datetime import datetime
from typing import Self
from pydantic import Field, model_validator
from src.repository.promotion.promotion_model import PromotionType
from src.schemas.base import BaseUpdateSchema
from src.schemas.promotion.create import PromotionConditionsSchema

class PromotionUpdateSchema(BaseUpdateSchema):
    id: int = Field(ge = 1)
    promo_type: PromotionType | None = None
    discount_value: int | None = Field(None, ge = 1)
    description: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    conditions: PromotionConditionsSchema | None = None
    is_active: bool | None = None
    archived: bool | None = None

    @model_validator(mode = "after")
    def validate_promotion(self) -> Self:
        if self.start_time is not None and self.end_time is not None and self.end_time <= self.start_time:
            raise ValueError("'end_time' has to be later than 'start_time'")

        if self.promo_type is not None and self.conditions is not None:
            is_bogo_condition = self.conditions.buy is not None or self.conditions.get is not None

            if self.promo_type == PromotionType.BOGO and not is_bogo_condition:
                raise ValueError("Promotion with type 'bogo' has to have conditions 'buy' and 'get'")

            if self.promo_type != PromotionType.BOGO and is_bogo_condition:
                raise ValueError("'buy' and 'get' acceptable only with promotion type 'bogo'")

        if self.promo_type == PromotionType.PERCENTAGE and self.discount_value and not (1 <= self.discount_value <= 100):
            raise ValueError("Promotion with type 'percentage' has to be in range 1 and 100")

        return self