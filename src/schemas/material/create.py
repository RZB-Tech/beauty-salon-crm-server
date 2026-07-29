from pydantic import BaseModel, ConfigDict, Field
from src.repository.material.material_model import MeasurementUnit

class MaterialCreateSchema(BaseModel):
    article: str = Field(max_length = 255)
    name: str = Field(max_length = 255)
    description: str | None = None

    quantity: int = Field(0, ge = 0)

    measurement_unit: MeasurementUnit = MeasurementUnit.PCS
    volume: int = Field(0, ge = 0)
    sell_price: int = Field(0, ge = 0)

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "article": "MAT-10023",
            "name": "Краска для волос",
            "description": "Стойкая краска, тон 5.0",
            "quantity": 20,
            "measurement_unit": "piece",
            "volume": 100,
            "sell_price": 50000
        }
    })