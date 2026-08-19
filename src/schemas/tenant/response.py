from datetime import datetime

from pydantic import BaseModel, ConfigDict
from src.schemas.base import ActorResponseSchema

class TenantIntegrationsResponseSchema(BaseModel):
    id: int

    telegram_bot_token: str | None = None

    created_at: datetime
    updated_at: datetime
    created_by: ActorResponseSchema | None = None

class TenantBranchResponseSchema(BaseModel):
    id: int
    name: str
    TIN: str | None = None
    parent_id: int | None = None
    active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes = True)

class TenantBranchCreateResponseSchema(BaseModel):
    tenant: TenantBranchResponseSchema
    login: str
    password: str