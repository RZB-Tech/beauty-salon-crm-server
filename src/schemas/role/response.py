from src.schemas.base import BaseResponseSchema

class RoleResponseSchema(BaseResponseSchema):
    name: str
    description: str | None = None
    permissions: list[int]