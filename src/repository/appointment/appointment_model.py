from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Integer,
    DateTime,
    Text,
    UniqueConstraint
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from src.database.base import BaseFields

if TYPE_CHECKING:
    from src.repository import Receipt

class AppointmentStatus(str, Enum):
    AWAITING = "awaiting"
    CANCELLED = "canceled"
    STARTED = "started"
    FINISHED = "finished"

class AppointmentServices(BaseFields):
    __tablename__ = "appointment_services"

    appointment_record_id: Mapped[int] = mapped_column(ForeignKey("appointment_records.id", ondelete = "CASCADE"))
    appointment_record: Mapped["AppointmentRecords"] = relationship(back_populates = "services")

    service_id: Mapped[int | None] = mapped_column(ForeignKey("services.id"), nullable = True)

    material_id: Mapped[int | None] = mapped_column(ForeignKey("materials.id"), nullable = True)

    quantity: Mapped[int] = mapped_column(Integer, default = 1)
    price: Mapped[int] = mapped_column(Integer, default = 0)
    price_changed_reason: Mapped[str | None] = mapped_column(Text, nullable = True)

    notes: Mapped[str | None] = mapped_column(Text, nullable = True)

class AppointmentRecords(BaseFields):
    __tablename__ = "appointment_records"

    appointment_id: Mapped[int] = mapped_column(ForeignKey("appointments.id", ondelete = "CASCADE"))
    appointment: Mapped["Appointment"] = relationship(back_populates = "records")

    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))

    services: Mapped[list[AppointmentServices]] = relationship(
        back_populates = "appointment_record", cascade = "all, delete-orphan"
    )

class Appointment(BaseFields):
    __tablename__ = "appointments"

    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))

    start_time_est: Mapped[datetime] = mapped_column(DateTime(timezone = True))
    end_time_est: Mapped[datetime] = mapped_column(DateTime(timezone = True))

    records: Mapped[list[AppointmentRecords]] = relationship(back_populates = "appointment",
                                                            cascade = "all, delete-orphan")

    status: Mapped[AppointmentStatus] = mapped_column(SQLEnum(
        AppointmentStatus, values_callable = lambda e: [m.value for m in e]), 
        default = AppointmentStatus.AWAITING)
    receipt: Mapped["Receipt"] = relationship(back_populates = "appointment")
    paid: Mapped[bool] = mapped_column(Boolean, default = False)
    notes: Mapped[str | None] = mapped_column(Text, nullable = True)

    __table_args__ = (
        UniqueConstraint("client_id", "start_time_est", "end_time_est", name="uq_client_appointment_time"),
        CheckConstraint("start_time_est < end_time_est", name="chk_start_before_end")
    )
    
    ALLOWED_FILTERS = {"client_id", "start_time_est", "end_time_est", "status", "paid"}

