from pydantic import BaseModel, ConfigDict, Field
from src.schemas.base import MoneyRequired

class ServiceCreateSchema(BaseModel):
    name: str = Field(max_length = 255)
    price: MoneyRequired
    category_id: int | None = Field(default = None, ge = 1)
    estimated_time: int | None = Field(default = None, ge = 1)

    model_config = ConfigDict(json_schema_extra = {
        "examples": [
            {
                "name": "Стрижка мужская",
                "price": 100000,
                "category_id": 1,
                "estimated_time": 30
            },
            {
                "name": "Женская стрижка",
                "price": 4253.54
            }
        ]
    })