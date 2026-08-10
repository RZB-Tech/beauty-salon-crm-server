from datetime import datetime
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.repository.promotion.promotion_model import PromotionType

class BuyGetItemSchema(BaseModel):
    object: Literal["service", "material"]
    id: int = Field(ge = 1)

class PromotionConditionsSchema(BaseModel):
    services: list[Annotated[int, Field(ge = 1)]] | None = Field(None, min_length = 1)
    materials: list[Annotated[int, Field(ge = 1)]] | None = Field(None, min_length = 1)
    buy: BuyGetItemSchema | None = None
    get: BuyGetItemSchema | None = None

    @model_validator(mode = "after")
    def validate_conditions(self) -> Self:
        has_scope = self.services is not None or self.materials is not None
        has_bogo = self.buy is not None or self.get is not None

        if has_bogo and (self.buy is None or self.get is None):
            raise ValueError("Required to specify 'buy' and 'get' for condition BOGO")

        if not has_scope and not has_bogo:
            raise ValueError("Required to specify at least either 'services' or 'materials' or 'buy'/'get' conditions")

        return self

class PromotionCreateSchema(BaseModel):
    name: str = Field(max_length = 255)
    promo_type: PromotionType
    discount_value: int | None = Field(None, ge = 1)
    description: str | None = None
    start_time: datetime
    end_time: datetime
    conditions: PromotionConditionsSchema
    is_active: bool | None = True

    @model_validator(mode = "after")
    def validate_promotion(self) -> Self:
        if self.end_time <= self.start_time:
            raise ValueError("'end_time' has to be later than 'start_time'")

        is_bogo_condition = self.conditions.buy is not None or self.conditions.get is not None

        if self.promo_type == PromotionType.BOGO and not is_bogo_condition:
            raise ValueError("Promotion with type 'bogo' has to have conditions 'buy' and 'get'")

        if self.promo_type != PromotionType.BOGO and is_bogo_condition:
            raise ValueError("'buy' and 'get' acceptable only with promotion type 'bogo'")

        if self.promo_type == PromotionType.PERCENTAGE and self.discount_value and not (1 <= self.discount_value <= 100):
            raise ValueError("Promotion with type 'percentage' has to be in range 1 and 100")
    
        return self

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "name": "Скидка на стрижки",
            "promo_type": "percentage",
            "discount_value": 15,
            "description": "Скидка 15% на все услуги из списка",
            "start_time": "2026-08-10T00:00:00Z",
            "end_time": "2026-09-10T00:00:00Z",
            "conditions": {
                "services": [1, 2, 3],
                "buy": {
                    "object": "service",
                    "id": 49
                },
                "get": {
                    "object": "service",
                    "id": 50
                }
            }
        }
    })