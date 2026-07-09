from pydantic import BaseModel

class TenantIntegrationsCreateSchema(BaseModel):
    telegram_bot_token: str | None = None