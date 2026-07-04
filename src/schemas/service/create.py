from pydantic import BaseModel, Field

class ServiceCreateSchema(BaseModel):
    name: str = Field(..., max_length = 255)
    price: int = Field(0, ge = 0)
    category_id: int | None = Field(None, ge = 1)