from datetime import datetime

from pydantic import BaseModel

from src.repository.transaction.transaction_model import TransactionCategory, TransactionMethod, TransactionType
from src.schemas.base import MoneyResponse

class SubscriptionPlanResponseSchema(BaseModel):
    id: int
    name: str
    description: str | None
    price: MoneyResponse
    max_branches: int
    max_users: int
    max_clients: int
    is_visible: bool

    created_at: datetime
    updated_at: datetime