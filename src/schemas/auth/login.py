from pydantic import BaseModel

from src.repository.staff.staff_model import StaffType
from src.schemas.base import BaseResponseSchema
from src.schemas.employee.response import EmployeeResponseBase

class LoginSchema(BaseModel):
    login: str
    password: str

class LoginResponseSchema(BaseResponseSchema):
    login: str
    employee: EmployeeResponseBase | None
    firstname: str | None
    lastname: str | None = None
    middlename: str | None = None
    active: bool
    staff_type: StaffType
    tenant_name: str