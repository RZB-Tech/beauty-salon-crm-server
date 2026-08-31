from pydantic import BaseModel

class EmployeeAnalyticsBaseResponse(BaseModel):
    employee_id: int
    appointments: int
    services: int
    revenue: int

class EmployeeAnalyticsResponse(BaseModel):
    items: list[EmployeeAnalyticsBaseResponse]