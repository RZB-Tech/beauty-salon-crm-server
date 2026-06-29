from pydantic import BaseModel, Field
from src.repository.material.material_model import MeasurementUnit

class MaterialCreateSchema(BaseModel):
    article: str = Field(max_length = 255)
    name: str = Field(max_length = 255)
    description: str | None = None

    quantity: int = Field(0, ge = 0)

    measurement_unit: MeasurementUnit = MeasurementUnit.PCS
    volume: int = Field(0, ge = 0)
    sell_price: int = Field(0, ge = 0)