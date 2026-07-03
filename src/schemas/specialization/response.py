from pydantic import Field
from src.schemas.base import BaseResponseSchema

class SpecializationResponseSchema(BaseResponseSchema):
    name: str = Field(..., max_length = 255)