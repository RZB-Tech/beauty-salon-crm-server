from datetime import datetime

from pydantic import BaseModel, ConfigDict

from src.schemas.base import MoneyResponse

class AddonPurchaseSchema(BaseModel):
    product_id: int

class AddonProductResponseSchema(BaseModel):
    id: int
    name: str
    description: str | None
    limit_key: str
    amount: int
    price: MoneyResponse

    model_config = ConfigDict(from_attributes = True)

class TenantAddonResponseSchema(BaseModel):
    id: int
    limit_key: str
    amount: int
    product_id: int | None
    expense_id: int | None
    expires_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes = True)

class AddonPurchaseResponseSchema(BaseModel):
    addon: TenantAddonResponseSchema
    tenant_balance: MoneyResponse
