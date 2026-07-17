from pydantic import BaseModel, Field, field_validator
from src.core.permissions import PERMISSIONS

class RoleCreateSchema(BaseModel):
    name: str = Field(max_length = 255)
    description: str | None = None
    permissions: list[int] = Field(default_factory = list)

    @field_validator("permissions")
    @classmethod
    def validate_permissions(cls, permissions: list[int]) -> list[int]:
        unknown = [code for code in permissions if code not in PERMISSIONS]
        if unknown:
            raise ValueError(f"Unknown permission codes: {unknown}")
        return permissions