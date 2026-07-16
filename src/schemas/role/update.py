from pydantic import Field, field_validator
from src.core.permissions import PERMISSIONS
from src.schemas.base import BaseUpdateSchema

class RoleUpdateSchema(BaseUpdateSchema):
    id: int = Field(ge = 1)
    name: str | None = Field(default = None, max_length = 255)
    description: str | None = None
    permissions: list[int] | None = None
    archived: bool | None = None

    @field_validator("permissions")
    @classmethod
    def validate_permissions(cls, permissions: list[int] | None) -> list[int] | None:
        if permissions is None:
            return permissions
        unknown = [code for code in permissions if code not in PERMISSIONS]
        if unknown:
            raise ValueError(f"Unknown permission codes: {unknown}")
        return permissions