from pydantic import Field, BaseModel

class ServiceCategoryUpdateSchema(BaseModel):
    id: int
    name: str = Field(..., max_length = 255)