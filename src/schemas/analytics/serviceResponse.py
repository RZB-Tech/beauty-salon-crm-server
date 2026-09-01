from pydantic import BaseModel

class ServiceAnalyticsBaseResponse(BaseModel):
    service_id: int
    service_name: str
    amount: int
    revenue: int

class ServiceAnalyticsResponse(BaseModel):
    items: list[ServiceAnalyticsBaseResponse]