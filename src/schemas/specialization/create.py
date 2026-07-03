from pydantic import BaseModel, Field

class SpecializationCreateSchema(BaseModel):
    name: str = Field(..., max_length = 255)