from __future__ import annotations
from typing import TYPE_CHECKING
from pydantic import BaseModel
from sqlalchemy import (
    Boolean,
    ForeignKey,
    String,
    Integer, Enum as SQLEnum, DateTime,
    func
)
from enum import Enum
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from src.database.base import Base

class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    name: Mapped[str] = mapped_column(String(255), unique = True)
    TIN: Mapped[int] = mapped_column(String(255), nullable = True)
    
    active: Mapped[bool] = mapped_column(Boolean)

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

class TenantSubscriptionStatus(Enum):
    ACTIVE = "active"
    CANCELLED = "canceled"
    TRIAL = "trial"
    PAST_DUE = "past due"

class TenantSubscriptions(Base):
    __tablename__ = "tenant_subscriptions"

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"))
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id"))
    status: Mapped[TenantSubscriptionStatus] = mapped_column(SQLEnum(
        TenantSubscriptionStatus, values_callable = lambda e: [m.value for m in e]))
    amount_paid: Mapped[int] = mapped_column(Integer, nullable = True)
    billing_interval: Mapped[int] = mapped_column()

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone = True))
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone = True))
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default = False)