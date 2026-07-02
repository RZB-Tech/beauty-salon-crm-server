from typing import Self

from fastapi import HTTPException
from pydantic import BaseModel, Field, model_validator

class StaffRequestSchema(BaseModel):
    id: int | None = Field(None, ge = 1)
    login: str | None = Field(None, min_length = 6)

    @model_validator(mode = "after")
    def require_at_leatst_one(self) -> Self:
        if self.id is None and self.login is None:
            raise HTTPException(400, "Необходимо указать id или login для поиска пользователя")
        
        if self.id and self.login:
            raise HTTPException(400, "Укажите только ID или логин")
        
class StaffUpdatePasswordSchema(BaseModel):
    id: int = Field(..., ge = 1)
    oldPassword: str = Field(..., min_length = 4)
    newPassword: str = Field(..., min_length = 4)

    @model_validator(mode = "after")
    def check_duplication(self) -> Self:
        if self.oldPassword == self.newPassword: 
            raise HTTPException(400, "Текущий и новый пароль одинаковы")