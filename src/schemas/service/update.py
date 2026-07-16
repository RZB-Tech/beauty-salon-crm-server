from pydantic import Field
from src.schemas.base import BaseUpdateSchema

class ServiceUpdateSchema(BaseUpdateSchema):
    id: int = Field(..., ge = 1)
    name: str | None = Field(None, max_length = 255)
    price: int | None = Field(None, ge = 1)
    estimated_time: int | None = Field(None, ge = 1)
    category_id: int | None = Field(None, ge = 1)
    archived: bool | None = None