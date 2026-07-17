from typing import Self

from fastapi import HTTPException
from pydantic import BaseModel, Field, field_validator, model_validator
from src.core.permissions import PERMISSIONS
from src.repository.staff.staff_model import StaffType

class StaffCreateBaseSchema(BaseModel):
    firstname: str | None = Field(None,  max_length = 255)
    lastname: str | None = Field(None, max_length = 255)
    middlename: str | None = Field(None, max_length = 255)
    login: str = Field(max_length = 100, min_length = 3)
    staff_type: StaffType = StaffType.EMPLOYEE
    permissions: list[int] | None = None
    roles: list[int] | None = None
    employee_id: int | None = Field(None, ge = 1)
    active: bool | None = None

    @field_validator("permissions")
    @classmethod
    def validate_permissions(cls, permissions: list[int] | None) -> list[int] | None:
        if permissions is None:
            return permissions
        unknown = [code for code in permissions if code not in PERMISSIONS]
        if unknown:
            raise ValueError(f"Unknown permission codes: {unknown}")
        return permissions

    @model_validator(mode = "after")
    def require_at_least_one(self) -> Self:
        if self.employee_id is None and self.firstname is None:
            raise HTTPException(400, "Необходимо указать имя или сотрудника для создания пользователя")
        return self

class StaffCreateAPISchema(StaffCreateBaseSchema):
    password: str | None = Field(None, max_length = 255, min_length = 6)