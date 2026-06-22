from pydantic import BaseModel, Field
from src.repository.material.material_model import MeasurementUnit

class MaterialCreateSchema(BaseModel):
    article: str = Field(max_length = 255)
    name: str = Field(max_length = 255)
    description: str | None = None

    quantity: int | None = 0

    measurement_unit: MeasurementUnit = MeasurementUnit.PCS
    volume: int | None = 0

    purchase_price: int | None = 0
    retail_price: int | None = 0 
    wholesale_price: int | None = 0 
    sell_price: int | None = 0 

    can_be_product: bool | None = False