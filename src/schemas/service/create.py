from pydantic import BaseModel, Field

class ServiceCreateSchema(BaseModel):
    name: str = Field(..., max_length = 255)
    category_id: int | None = None