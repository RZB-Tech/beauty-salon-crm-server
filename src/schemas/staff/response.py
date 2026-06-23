from src.schemas.base import BaseResponseSchema

class StaffResponseSchema(BaseResponseSchema):
    login: str
    employee_id: int | None = None
    active: bool
    firstname: str
    lastname: str | None = None
    middlename: str | None = None