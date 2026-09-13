from pydantic import BaseModel

from src.schemas.base import MoneyResponse

class EmployeeAnalyticsBaseResponse(BaseModel):
    employee_id: int
    employee_fullname: str
    appointments: int
    services: int
    revenue: MoneyResponse

class EmployeeAnalyticsResponse(BaseModel):
    items: list[EmployeeAnalyticsBaseResponse]