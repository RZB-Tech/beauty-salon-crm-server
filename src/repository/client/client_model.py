from __future__ import annotations
from decimal import Decimal
from enum import StrEnum
from sqlalchemy import (
    ForeignKey,
    Numeric,
    String,
    Integer,
    Date,
    Text,
    ForeignKeyConstraint,
    UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date
from src.database.base import BaseFields

class Sex(StrEnum):
    MALE = "male"
    FEMALE = "female"

class Client(BaseFields):
    __tablename__ = "clients"

    firstname: Mapped[str] = mapped_column(String(255))
    lastname: Mapped[str | None] = mapped_column(String(255), nullable=True)
    middlename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable = True)
    sex: Mapped[str] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(Text, nullable = True)
    deposit: Mapped[Decimal] = mapped_column(Numeric(precision = 30, scale = 2), default = 0)

    global_client_id: Mapped[int | None] = mapped_column(
        ForeignKey("global_clients.id", ondelete = "SET NULL"), nullable = True, index = True)

    __table_args__ = (
        UniqueConstraint("id", "tenant_id", name = "uq_client_tenant"),
        UniqueConstraint("firstname", "lastname", "middlename", "birth_date" ,"phone", "tenant_id", name = "uq_client_per_tenant"),
        UniqueConstraint("global_client_id", "tenant_id", name = "uq_client_global_client_tenant"),
        ForeignKeyConstraint(
            ["created_by_actor_id", "tenant_id"],
            ["actors.id", "actors.tenant_id"],
            ondelete = "SET NULL (created_by_actor_id)",
            name = "fk_clients_created_by_tenant"
        ),
    )

    ALLOWED_FILTERS = {"firstname", "lastname", "middlename", "phone", "birth_date", "sex", "archived"}