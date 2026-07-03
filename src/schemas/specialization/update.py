from pydantic import Field
from src.schemas.base import BaseUpdateSchema

class SpecializationUpdateSchema(BaseUpdateSchema):
    id: int
    name: str = Field(..., max_length = 255)