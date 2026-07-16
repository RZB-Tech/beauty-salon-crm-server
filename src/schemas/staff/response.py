from src.schemas.base import BaseResponseSchema
from src.schemas.role.response import RoleResponseSchema

class StaffResponseSchema(BaseResponseSchema):
    login: str
    employee_id: int | None = None
    active: bool
    firstname: str
    lastname: str | None = None
    middlename: str | None = None
    permissions: list[int] = []
    roles: list[RoleResponseSchema] = []

class StaffCreateResponseSchema(StaffResponseSchema):
    password: str
