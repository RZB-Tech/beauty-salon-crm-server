from src.repository.material.material_model import MeasurementUnit
from src.schemas.base import BaseResponseSchema, MoneyRequired, MoneyResponse

class MaterialResponseSchema(BaseResponseSchema):
    article: str
    name: str
    description: str | None = None

    quantity: int

    measurement_unit: MeasurementUnit
    volume: int

    sell_price: MoneyRequired