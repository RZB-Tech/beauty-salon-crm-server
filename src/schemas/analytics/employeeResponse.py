from pydantic import BaseModel

class EmployeeAnalyticsBaseResponse(BaseModel):
    employee_id: int
    employee_fullname: str
    appointments: int
    services: int
    revenue: int

class EmployeeAnalyticsResponse(BaseModel):
    items: list[EmployeeAnalyticsBaseResponse]