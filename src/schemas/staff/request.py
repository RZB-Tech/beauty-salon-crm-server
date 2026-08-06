from typing import Self
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from src.core.permissions import PERMISSIONS

class StaffRequestSchema(BaseModel):
    id: int | None = Field(None, ge = 1)
    login: str | None = Field(None, min_length = 6)

    @model_validator(mode = "after")
    def require_at_leatst_one(self) -> Self:
        if self.id is None and self.login is None:
            raise ValueError("Required to specify either 'id' or 'login' to find user")

        if self.id and self.login:
            raise ValueError("Specify either 'id' or 'login'")

        return self
class StaffUpdatePasswordSchema(BaseModel):
    id: int | None = Field(None, ge = 1)
    oldPassword: str = Field(..., min_length = 4)
    newPassword: str = Field(..., min_length = 6)

    @model_validator(mode = "after")
    def check_duplication(self) -> Self:
        if self.oldPassword == self.newPassword:
            raise ValueError("Current and new passwords are identical")
        return self

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "oldPassword": "OldSecurePass123!",
            "newPassword": "NewSecurePass456!"
        }
    })

class StaffRolesAssignSchema(BaseModel):
    id: int = Field(..., ge = 1)
    role_ids: list[int] = Field(default_factory = list)

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "id": 1,
            "role_ids": [1, 2]
        }
    })

class StaffPermissionsUpdateSchema(BaseModel):
    id: int = Field(..., ge = 1)
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
            "id": 1,
            "permissions": [3001, 3002]
        }
    })