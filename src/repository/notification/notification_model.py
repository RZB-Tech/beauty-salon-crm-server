from __future__ import annotations
from datetime import datetime
from enum import Enum, StrEnum
from typing import TYPE_CHECKING
from sqlalchemy import (
    ForeignKeyConstraint,
    DateTime,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column
from src.database.base import BaseFields

class NotificationType(StrEnum):
    REMINDER = "reminder"
    OTHER = "other"

class NotificationStatus(StrEnum):
    PENDING = "pending"
    READ = "read"
    CANCELLED = "cancelled"

class Notification(BaseFields):
    __tablename__ = "notifications"

    client_id: Mapped[int | None] = mapped_column(Integer, nullable = True)
    title: Mapped[str | None] = mapped_column(String(50), nullable = True)
    body: Mapped[str] = mapped_column(Text)

    type: Mapped[str] = mapped_column(String(50))

    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone = True))
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone = True), nullable = True, default = None)
    status: Mapped[str] = mapped_column(String(50), default = NotificationStatus.PENDING)

    notes: Mapped[str | None] = mapped_column(Text, nullable = True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["client_id", "tenant_id"],
            ["clients.id", "clients.tenant_id"],
            ondelete = "CASCADE",
            name = "fk_notifications_client_tenant"
        ),
    )

    ALLOWED_FILTERS = {"client_id", "type", "scheduled_at", "delivered_at", "archived", "status"}