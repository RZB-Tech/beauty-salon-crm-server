from pydantic import Field, BaseModel

from src.schemas.base import BaseUpdateSchema

class ServiceCategoryUpdateSchema(BaseUpdateSchema):
    id: int
    name: str | None = Field(None, max_length = 255)
    archived: bool | None = None