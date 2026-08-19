from pydantic import BaseModel

class TenantIntegrationsCreateSchema(BaseModel):
    telegram_bot_token: str | None = None

class TenantBranchCreateSchema(BaseModel):
    company_name: str
    company_tin: str | None = None
    admin_login: str
    admin_firstname: str
    admin_password: str | None = None