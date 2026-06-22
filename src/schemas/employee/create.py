from datetime import date
from pydantic import BaseModel, ConfigDict, Field

class EmployeeCreateSchema(BaseModel):
    firstname: str = Field(..., max_length=100, description="Employee's first name")
    lastname: str | None = Field(None, max_length=100)
    middlename: str | None = Field(None, max_length=100)
    phone: str | None = Field(None, max_length=50)
    birth_date: date
    active: bool = True
    specialization_id: int | None = None
    services_ids: list[int] = Field(default_factory = list)
    salary_fixed: int | None = 0
    percent_from_services: int | None = 0
    percent_from_sales: int | None = 0