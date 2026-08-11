from datetime import datetime
from typing import Self
from pydantic import ConfigDict, Field, model_validator
from src.repository.promotion.promotion_model import PromotionType
from src.schemas.base import BaseUpdateSchema

class PromotionUpdateSchema(BaseUpdateSchema):
    id: int = Field(ge = 1)
    name: str | None = Field(None, max_length = 255)
    promo_type: PromotionType | None = None
    service_id: int | None = Field(None, ge = 1)
    material_id: int | None = Field(None, ge = 1)
    discount_value: int | None = Field(None, ge = 1) 
    description: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    is_active: bool | None = None
    archived: bool | None = None

    @model_validator(mode = "after")
    def validate_promotion(self) -> Self:
        if self.start_time is not None and self.end_time is not None and self.end_time <= self.start_time:
            raise ValueError("'end_time' has to be later than 'start_time'")

        if self.promo_type == PromotionType.PERCENTAGE and self.discount_value and not (1 <= self.discount_value <= 100):
            raise ValueError("Promotion with type 'percentage' has to be in range 1 and 100")

        return self

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "name": "Летняя скидка",
            "promo_type": "percentage",
            "service_id": 1,
            "discount_value": 15,
            "description": "Скидка 15%",
            "start_time": "2026-08-10T00:00:00Z",
            "end_time": "2026-09-10T00:00:00Z",
        }
    })