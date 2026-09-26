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

class TenantSubscriptionInfoSchema(BaseModel):
    id: int
    plan_id: int
    status: str
    amount_paid: MoneyResponse | None
    started_at: datetime
    period_end: datetime

    model_config = ConfigDict(from_attributes = True)

class TenantBillingStateSchema(BaseModel):
    balance: MoneyResponse
    has_active_subscription: bool
    subscription: TenantSubscriptionInfoSchema | None

class TenantLimitUsageSchema(BaseModel):
    limit_key: str
    plan: int | None
    addons: int
    allowed: int | None
    used: int
    remaining: int | None

class TenantLimitsSchema(BaseModel):
    plan_id: int | None
    can_create_branches: bool
    limits: list[TenantLimitUsageSchema]
