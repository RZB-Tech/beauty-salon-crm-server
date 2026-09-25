from __future__ import annotations
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    Numeric,
    String,
    DateTime,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, CITEXT
from enum import StrEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from src.database.base import Base, BaseFields

if TYPE_CHECKING:
    from src.repository.tenant.subscription.subscriptionPlan_model import SubscriptionPlan

class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    name: Mapped[str] = mapped_column(CITEXT, index = True)
    TIN: Mapped[str] = mapped_column(String(255), nullable = True)

    active: Mapped[bool] = mapped_column(Boolean, default = True, server_default="true")
    preferences: Mapped[dict] = mapped_column(JSONB, default = dict)
    balance: Mapped[Decimal] = mapped_column(Numeric(precision = 30, scale = 2), default = 0, server_default = text("0"))

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

    __table_args__ = (
        CheckConstraint("balance >= 0", "tenant_balance_non_negative"),
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