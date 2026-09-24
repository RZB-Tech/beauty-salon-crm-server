from pydantic import BaseModel

class TenantSubscriptionPurchaseSchema(BaseModel):
    plan_id: int
