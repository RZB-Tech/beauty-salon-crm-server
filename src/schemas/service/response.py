from pydantic import ConfigDict

from src.schemas.base import BaseResponseSchema

class ServiceResponseSchema(BaseResponseSchema):
    name: str
    price: int
    category_id: int | None
    
    model_config = ConfigDict(from_attributes=True)