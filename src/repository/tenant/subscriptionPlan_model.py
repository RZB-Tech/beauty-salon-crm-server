from __future__ import annotations
from decimal import Decimal
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Numeric,
    String,
    Integer,
    Text
)
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    name: Mapped[str] = mapped_column(String(255), unique = True)
    description: Mapped[str] = mapped_column(Text, nullable = True)

    price: Mapped[Decimal] = mapped_column(Numeric(precision = 30, scale = 2))

    max_branches: Mapped[int] = mapped_column(Integer, nullable = True, default = 1)
    max_users: Mapped[int] = mapped_column(Integer, nullable = True, default = 3)
    max_clients: Mapped[int] = mapped_column(Integer, nullable = True, default = 500)
    max_archive_period: Mapped[int] = mapped_column(Integer, nullable = True, default = 12) # in months

    is_visible: Mapped[bool] = mapped_column(Boolean, default = False)

    __table_args__ = (
        CheckConstraint("max_branches >= 1", "subscripition_plan_max_branches"),
        CheckConstraint("max_users >= 1", "subscripition_plan_max_users"),
        CheckConstraint("max_clients >= 1", "subscripition_plan_max_clients")
    )

    def __str__(self) -> str:
        return f"{self.name} ({self.id})"