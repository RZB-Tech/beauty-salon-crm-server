from datetime import datetime

from pydantic import BaseModel
from src.schemas.base import ActorResponseSchema

class TenantIntegrationsResponseSchema(BaseModel):
    id: int

    telegram_bot_token: str | None = None

    created_at: datetime
    updated_at: datetime
    created_by: ActorResponseSchema | None = None