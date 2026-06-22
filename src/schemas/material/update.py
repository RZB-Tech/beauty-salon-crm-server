from enum import IntEnum

from pydantic import BaseModel, Field
from src.repository.material.material_model import MeasurementUnit
from src.schemas.base import BaseUpdateSchema

class MaterialUpdateSchema(BaseUpdateSchema):
    id: int

    article: str | None = Field(default = None, max_digits = 255)
    name: str | None = Field(default = None, max_digits = 255)
    description: str | None = None

    measurement_unit: MeasurementUnit | None = None
    volume: int | None = None

    purchase_price: int | None = None
    retail_price: int | None = None 
    wholesale_price: int | None = None 
    sell_price: int | None = None 

    can_be_product: bool | None = None

class MaterialOperation(IntEnum):
    INCREMENT = 1
    DECREMENT = -1

class MaterialQuantityUpdateSchema(BaseModel):
    id: int = Field(ge = 1)
    operation: MaterialOperation
    quantity: int = Field(ge = 1)