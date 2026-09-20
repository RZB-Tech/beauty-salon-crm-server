from __future__ import annotations
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import (
    Boolean,
    ForeignKey,
    ForeignKeyConstraint,
    Numeric,
    String,
    DateTime,
    Text,
    func,
    UniqueConstraint
)
from sqlalchemy.dialects.postgresql import JSONB, CITEXT
from enum import StrEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from src.database.base import Base, BaseFields

if TYPE_CHECKING:
    from src.repository.tenant.subscriptionPlan_model import SubscriptionPlan

class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    name: Mapped[str] = mapped_column(CITEXT, index = True)
    TIN: Mapped[str] = mapped_column(String(255), nullable = True)

    active: Mapped[bool] = mapped_column(Boolean, default = True, server_default="true")
    preferences: Mapped[dict] = mapped_column(JSONB, default = dict)
    balance: Mapped[Decimal] = mapped_column(Numeric(precision = 30, scale = 2), default = 0)

    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("tenants.id", ondelete = "RESTRICT"), nullable = True, index = True
    )

    # Deliberately a plain FK to actors.id, not the usual (actor_id, tenant_id)
    # composite - the creator is the parent tenant's actor, not this tenant's,
    # so pairing it with this row's own id would never match.
    created_by_actor_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "actors.id", ondelete = "SET NULL", use_alter = True,
            name = "fk_tenants_created_by_actor_id",
        ),
        nullable = True, index = True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    integration: Mapped["TenantIntegration | None"] = relationship(
        viewonly = True,
        uselist = False,
        primaryjoin = "Tenant.id == TenantIntegration.tenant_id",
    )

    parent: Mapped["Tenant | None"] = relationship(
        "Tenant", remote_side = [id], back_populates = "branches"
    )
    branches: Mapped[list["Tenant"]] = relationship(
        "Tenant", back_populates = "parent"
    )

    def __str__(self) -> str:
        return f"{self.name} ({self.id})"

class TenantIntegration(BaseFields):
    __tablename__ = "tenant_integrations"

    telegram_bot_token: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["created_by_actor_id", "tenant_id"],
            ["actors.id", "actors.tenant_id"],
            ondelete = "SET NULL (created_by_actor_id)",
            name = "fk_tenant_integrations_created_by_tenant"
        ),
    )

class TenantSubscriptionStatus(StrEnum):
    ACTIVE = "active"
    CANCELLED = "canceled"
    TRIAL = "trial"
    PAST_DUE = "past due"

class TenantSubscriptions(Base):
    __tablename__ = "tenant_subscriptions"

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id", ondelete = "cascade"), unique = True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("subscription_plans.id", ondelete = "restrict"))
    status: Mapped[str] = mapped_column(String(50))
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(precision = 30, scale = 2), nullable = True)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone = True))
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone = True))

    tenant: Mapped["Tenant"] = relationship(foreign_keys = [tenant_id])
    plan: Mapped["SubscriptionPlan"] = relationship("SubscriptionPlan", foreign_keys = [plan_id])

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

class TenantPayments(Base):
    __tablename__ = "tenant_payments"

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id", ondelete = "set null"), nullable = True)
    tenant_snapshot: Mapped[dict] = mapped_column(JSONB)
    amount: Mapped[Decimal] = mapped_column(Numeric(precision = 30, scale = 2))
    gateway: Mapped[str | None] = mapped_column(String(255), nullable = True)
    gateway_transaction_id: Mapped[str | None] = mapped_column(String(255), nullable = True)
    gateway_metadata: Mapped[dict] = mapped_column(JSONB, default = dict)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("gateway", "gateway_transaction_id", name = "uq_tenant_payments_gateway_transaction"),
    )

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