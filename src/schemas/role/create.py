from pydantic import BaseModel, ConfigDict, Field, field_validator
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
            raise ValueError(f"Unknown permissions: {unknown}")
        return permissions

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "name": "Администратор филиала",
            "description": "Полный доступ к записям и финансам филиала",
            "permissions": [2003, 2005, 3003, 3006]
        }
    })