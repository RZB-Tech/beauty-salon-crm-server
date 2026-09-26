from __future__ import annotations
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.base import BaseFields

if TYPE_CHECKING:
    from src.repository import Appointment, GlobalClient

class AppointmentRequestStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    DECLINED = "declined"
    CANCELLED = "cancelled"

class AppointmentRequestCancelledReason(StrEnum):
    CLIENT_CANCELLED = "cancelled by client"
    PAST_DUE = "automatically: time to make action passed"

class AppointmentRequest(BaseFields):
    """
    A client's request (from the Telegram mini app) to book an appointment at a tenant:
    services with quantities and a desired start time - the client sees no schedules.
    Becomes an Appointment (created_via = telegram) only when the tenant's staff
    confirms it, choosing the actual time, employees and services.
    """
    __tablename__ = "appointment_requests"

    global_client_id: Mapped[int] = mapped_column(
        ForeignKey("global_clients.id", ondelete = "CASCADE"), index = True)
    global_client: Mapped["GlobalClient"] = relationship(lazy = "joined", innerjoin = True)

    # [{"service_id", "name", "price", "estimated_time", "quantity"}, ...] as the client saw
    # them when requesting - survives the services being edited or deleted later
    services: Mapped[list[dict]] = mapped_column(JSONB)

    start_time_est: Mapped[datetime] = mapped_column(DateTime(timezone = True))
    # Estimate only: start + the services' durations x quantity. Staff set the real times on confirm.
    end_time_est: Mapped[datetime] = mapped_column(DateTime(timezone = True))
    comment: Mapped[str | None] = mapped_column(Text, nullable = True)

    status: Mapped[str] = mapped_column(String(50), default = AppointmentRequestStatus.PENDING)
    cancelled_reason: Mapped[str | None] = mapped_column(String(50), nullable = True)
    # Optional free-text reason the client gives when cancelling
    cancel_comment: Mapped[str | None] = mapped_column(Text, nullable = True)
    # Required when staff decline; shown to the client
    decline_reason: Mapped[str | None] = mapped_column(Text, nullable = True)

    # Pending request is auto-cancelled after this moment (see appointmentRequest_task.py)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone = True))
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone = True), nullable = True)

    appointment_id: Mapped[int | None] = mapped_column(Integer, nullable = True)
    appointment: Mapped["Appointment | None"] = relationship(
        primaryjoin = "and_(AppointmentRequest.appointment_id == Appointment.id, AppointmentRequest.tenant_id == Appointment.tenant_id)",
        foreign_keys = [appointment_id],
        viewonly = True,
        lazy = "selectin"
    )

    __table_args__ = (
        UniqueConstraint("id", "tenant_id", name = "uq_appointment_request_tenant"),
        ForeignKeyConstraint(
            ["appointment_id", "tenant_id"],
            ["appointments.id", "appointments.tenant_id"],
            ondelete = "SET NULL (appointment_id)",
            name = "fk_appointment_requests_appointment"
        ),
        ForeignKeyConstraint(
            ["created_by_actor_id", "tenant_id"],
            ["actors.id", "actors.tenant_id"],
            ondelete = "SET NULL (created_by_actor_id)",
            name = "fk_appointment_requests_created_by_tenant"
        ),
        CheckConstraint("start_time_est < end_time_est", name = "chk_appointment_request_start_before_end"),
        Index("ix_appointment_requests_status_expires_at", "status", "expires_at"),
    )

    ALLOWED_FILTERS = {"global_client_id", "start_time_est", "end_time_est", "status", "expires_at", "archived"}
