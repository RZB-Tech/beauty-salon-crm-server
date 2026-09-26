from datetime import datetime
from pydantic import BaseModel
from src.schemas.base import MoneyResponse

class SubscriptionPlanResponseSchema(BaseModel):
    id: int
    name: str
    description: str | None
    price: MoneyResponse
    duration_days: int
    max_users: int | None
    max_clients: int | None
    can_create_branches: bool
    is_visible: bool

    created_at: datetime
    updated_at: datetime