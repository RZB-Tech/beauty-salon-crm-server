from pydantic import Field
from src.schemas.base import BaseUpdateSchema

class SpecializationUpdateSchema(BaseUpdateSchema):
    id: int = Field(ge = 1)
    name: str | None = Field(None, max_length = 255)
    archived: bool | None = None