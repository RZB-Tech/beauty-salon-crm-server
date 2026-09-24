from datetime import datetime

from pydantic import BaseModel, ConfigDict

from src.schemas.base import MoneyResponse

class TenantSubscriptionResponseSchema(BaseModel):
    id: int
    tenant_id: int
    plan_id: int
    status: str
    amount_paid: MoneyResponse
    started_at: datetime
    period_end: datetime
    tenant_balance: MoneyResponse

    model_config = ConfigDict(from_attributes = True)
