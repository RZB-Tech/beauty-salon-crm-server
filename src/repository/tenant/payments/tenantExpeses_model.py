from __future__ import annotations
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import (
    ForeignKey,
    Numeric,
    String,
    DateTime,
    Text,
    func
)
from sqlalchemy.dialects.postgresql import JSONB
from enum import StrEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from src.database.base import Base

if TYPE_CHECKING:
    from src.repository.tenant.tenant_model import Tenant

class TenantExpenseCategory(StrEnum):
    SUBSCRIPTION = "subscription"
    FEATURE_PURCHASE = "feature purchase"
    OTHER = "other"

class TenantExpenses(Base):
    __tablename__ = "tenant_expenses"

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    tenant_id: Mapped[int | None] = mapped_column(ForeignKey("tenants.id", ondelete = "set null"), nullable = True)
    tenant_snapshot: Mapped[dict] = mapped_column(JSONB)
    amount: Mapped[Decimal] = mapped_column(Numeric(precision = 30, scale = 2))
    category: Mapped[str] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(Text, nullable = True)
    expense_metadata: Mapped[dict] = mapped_column(JSONB, default = dict)

    tenant: Mapped["Tenant | None"] = relationship(foreign_keys = [tenant_id])

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )