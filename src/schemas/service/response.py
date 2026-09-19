from pydantic import ConfigDict
from src.schemas.base import BaseResponseSchema, MoneyRequired

class ServiceResponseSchema(BaseResponseSchema):
    name: str
    price: MoneyRequired
    category_id: int | None
    estimated_time: int
    
    model_config = ConfigDict(from_attributes=True)