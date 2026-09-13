from pydantic import BaseModel

from src.schemas.base import MoneyResponse

class ServiceAnalyticsBaseResponse(BaseModel):
    service_id: int
    service_name: str
    amount: MoneyResponse
    revenue: MoneyResponse

class ServiceAnalyticsResponse(BaseModel):
    items: list[ServiceAnalyticsBaseResponse]