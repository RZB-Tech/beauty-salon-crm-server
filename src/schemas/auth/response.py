from src.repository.staff.staff_model import StaffType
from src.schemas.base import BaseResponseSchema
from src.schemas.employee.response import EmployeeResponseBase

class MeResponseSchema(BaseResponseSchema):
    login: str
    employee: EmployeeResponseBase | None
    firstname: str | None
    lastname: str | None = None
    middlename: str | None = None
    active: bool
    staff_type: StaffType