from __future__ import annotations
from decimal import Decimal
from sqlalchemy import (
    Boolean,
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

    max_employees: Mapped[int] = mapped_column(Integer)
    max_clients: Mapped[int] = mapped_column(Integer)
    max_services: Mapped[int] = mapped_column(Integer)
    max_materials: Mapped[int] = mapped_column(Integer)
    max_archive_period: Mapped[int] = mapped_column(Integer, default = 1) # in months

    is_visible: Mapped[bool] = mapped_column(Boolean, default = False)