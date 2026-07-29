from pydantic import BaseModel, ConfigDict, Field

class ServiceCreateSchema(BaseModel):
    name: str = Field(..., max_length = 255)
    price: int = Field(0, ge = 0)
    category_id: int | None = Field(None, ge = 1)
    estimated_time: int | None = Field(None, ge = 1)

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "name": "Стрижка мужская",
            "price": 100000,
            "category_id": 1,
            "estimated_time": 30
        }
    })