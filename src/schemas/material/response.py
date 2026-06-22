from src.repository.material.material_model import MeasurementUnit
from src.schemas.base import BaseResponseSchema

class MaterialResponseSchema(BaseResponseSchema):
    article: str
    name: str
    description: str | None = None

    quantity: int

    measurement_unit: MeasurementUnit
    volume: int

    purchase_price: int
    retail_price: int 
    wholesale_price: int 
    sell_price: int 

    can_be_product: bool