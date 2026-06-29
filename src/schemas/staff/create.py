from typing import Self

from fastapi import HTTPException
from pydantic import BaseModel, Field, model_validator

class StaffCreateBaseSchema(BaseModel):
    firstname: str | None = Field(None,  max_length=255)
    lastname: str | None = Field(None, max_length=255)
    middlename: str | None = Field(None, max_length=255)
    login: str = Field(max_length = 100)
    employee_id: int | None = Field(None, ge = 1)
    active: bool | None = None

    @model_validator(mode = "after")
    def require_at_least_one(self) -> Self:
        if self.employee_id is None and self.firstname is None:
            raise HTTPException(400, "Необходимо указать имя или сотрудника для создания пользователя")

class StaffCreateAPISchema(StaffCreateBaseSchema):
    password: str = Field(max_length = 255, min_length = 6)