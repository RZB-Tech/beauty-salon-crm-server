from pydantic import Field, BaseModel

from src.schemas.base import BaseUpdateSchema

class ServiceCategoryUpdateSchema(BaseUpdateSchema):
    id: int = Field(..., ge = 1)
    name: str | None = Field(None, max_length = 255)