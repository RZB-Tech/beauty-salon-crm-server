from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Integer,
    Text,
    func,
    text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

if TYPE_CHECKING:
    from src.repository.tenant.tenant_model import Tenant
    from src.repository.tenant.payments.tenantExpeses_model import TenantExpenses

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    name: Mapped[str] = mapped_column(String(255), unique = True)
    description: Mapped[str | None] = mapped_column(Text, nullable = True)

    price: Mapped[Decimal] = mapped_column(Numeric(precision = 30, scale = 2))
    duration_days: Mapped[int] = mapped_column(Integer)

    max_branches: Mapped[int] = mapped_column(Integer, nullable = True, default = 1)
    max_users: Mapped[int] = mapped_column(Integer, nullable = True, default = 3)
    max_clients: Mapped[int] = mapped_column(Integer, nullable = True, default = 500)

    is_visible: Mapped[bool] = mapped_column(Boolean, default = False)
    archived: Mapped[bool] = mapped_column(Boolean, default = False, server_default = text("false"))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        )

    __table_args__ = (
        CheckConstraint("max_branches >= 1", "subscripition_plan_max_branches"),
        CheckConstraint("max_users >= 1", "subscripition_plan_max_users"),
        CheckConstraint("max_clients >= 1", "subscripition_plan_max_clients"),
        CheckConstraint("duration_days >= 1", "subscripition_plan_duration_days"),
        CheckConstraint("price >= 0", "subscripition_plan_price_non_negative"),
    )

    def __str__(self) -> str:
        return f"{self.name} ({self.id})"

class TenantAddon(Base):
    __tablename__ = "tenant_addons"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id", ondelete="cascade"))
    limit_key: Mapped[str] = mapped_column(String(50))
    amount: Mapped[int] = mapped_column(Integer)
    expense_id: Mapped[int | None] = mapped_column(ForeignKey("tenant_expenses.id"), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    tenant: Mapped["Tenant"] = relationship(foreign_keys=[tenant_id])
    expense: Mapped["TenantExpenses | None"] = relationship(foreign_keys=[expense_id])

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())