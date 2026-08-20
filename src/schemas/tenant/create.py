from typing import Self
from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.core.utils.common import validate_contain_only_alpha_and_digits

class TenantIntegrationsCreateSchema(BaseModel):
    telegram_bot_token: str | None = None

class TenantBranchCreateSchema(BaseModel):
    company_name: str
    company_tin: str | None = None
    admin_login: str
    admin_firstname: str
    admin_password: str | None = None

    @field_validator("admin_login")
    @classmethod
    def validate_admin_login(cls, v: str) -> str:
        if not validate_contain_only_alpha_and_digits(v):
            raise ValueError("`admin_login` has to contain only alphabetic characters or digits (0-9)")
        return v.lower()

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "company_name": "Z-company",
            "company_tin": "3342421123",
            "admin_login": "aleksandr",
            "admin_firstname": "makedonian",
            "admin_password": "theGreat"
        }
    })

class BranchAdminCreateSchema(BaseModel): 
    branch_id: int = Field(ge = 1)
    admin_login: str
    admin_firstname: str
    admin_password: str | None = None

    @field_validator("admin_login")
    @classmethod
    def validate_admin_login(cls, v: str) -> str:
        if not validate_contain_only_alpha_and_digits(v):
            raise ValueError("`admin_login` has to contain only alphabetic characters or digits (0-9)")
        return v.lower()

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "branch_id": 1,
            "admin_login": "aleksandr",
            "admin_firstname": "makedonian",
            "admin_password": "theGreat"
        }
    })