from src.schemas.base import BaseUpdateSchema
from pydantic import Field
from datetime import date

class EmployeeUpdateSchema(BaseUpdateSchema):
    id: int = Field(ge = 1)
    firstname: str | None = None
    lastname: str | None = None
    middlename: str | None = None
    phone: str | None = None
    birth_date: date | None = None
    specialization_id: int | None = None
    services: list[int] | None = None

    salary_fixed: int | None = Field(default = None, ge = 1)
    percent_from_services: int | None = Field(default = None, ge = 1)
    percent_from_sales: int | None = Field(default = None, ge = 1)
    notes: str | None = None