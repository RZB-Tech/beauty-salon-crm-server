from pydantic import BaseModel, Field

class ServiceCategoryCreateSchema(BaseModel):
    name: str = Field(..., max_length = 255)