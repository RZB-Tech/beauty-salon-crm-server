from __future__ import annotations
from enum import Enum, StrEnum
from typing import TYPE_CHECKING
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKeyConstraint,
    Integer,
    DateTime,
    String,
    Text,
    UniqueConstraint
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from src.database.base import BaseFields

if TYPE_CHECKING:
    from src.repository import Receipt, Client, Employee, Service, Material

class AppointmentStatus(StrEnum):
    AWAITING = "awaiting"
    CANCELLED = "cancelled"
    STARTED = "started"
    FINISHED = "finished"

class AppointmentCancelledReason(StrEnum):
    CLIENT_CANCELLED = "client changed his mind"
    MISTAKEN_INPUT = "mistaken input"
    INCORRECT_CLIENT = "incorrect client"
    INCORRECT_DATE = "incorrect date"

class AppointmentServices(BaseFields):
    __tablename__ = "appointment_services"

    appointment_record_id: Mapped[int] = mapped_column(Integer)
    appointment_record: Mapped["AppointmentRecords"] = relationship(
        back_populates = "services",
        primaryjoin = "and_(AppointmentServices.appointment_record_id == AppointmentRecords.id, AppointmentServices.tenant_id == AppointmentRecords.tenant_id)",
        foreign_keys = [appointment_record_id])

    service_id: Mapped[int | None] = mapped_column(Integer, nullable = True)
    service: Mapped["Service"] = relationship(
        primaryjoin="and_(AppointmentServices.service_id == Service.id, AppointmentServices.tenant_id == Service.tenant_id)",
        foreign_keys=[service_id]
    )
    material_id: Mapped[int | None] = mapped_column(Integer, nullable = True)
    material: Mapped["Material"] = relationship(
        primaryjoin="and_(AppointmentServices.material_id == Material.id, AppointmentServices.tenant_id == Material.tenant_id)",
        foreign_keys=[material_id]
    )

    quantity: Mapped[int] = mapped_column(Integer, default = 1)
    price: Mapped[int] = mapped_column(Integer, default = 0)
    price_changed_reason: Mapped[str | None] = mapped_column(Text, nullable = True)

    notes: Mapped[str | None] = mapped_column(Text, nullable = True)

    __table_args__ = (
        UniqueConstraint("id", "tenant_id", name = "fk_appointment_services_tenant"),
        ForeignKeyConstraint(
            ["service_id", "tenant_id"],
            ["services.id", "services.tenant_id"],
            ondelete = "RESTRICT",
            name = "fk_appointment_services_serivce"
        ),
        ForeignKeyConstraint(
            ["material_id", "tenant_id"],
            ["materials.id", "materials.tenant_id"],
            ondelete = "RESTRICT",
            name = "fk_appointment_services_material"
        ),
        ForeignKeyConstraint(
            ["appointment_record_id", "tenant_id"],
            ["appointment_records.id", "appointment_records.tenant_id"],
            ondelete = "CASCADE",
            name = "fk_appointment_services_record"
        ),
    )

class AppointmentRecords(BaseFields):
    __tablename__ = "appointment_records"

    appointment_id: Mapped[int] = mapped_column(Integer)
    appointment: Mapped["Appointment"] = relationship(
        back_populates = "records",
        primaryjoin = "and_(AppointmentRecords.appointment_id == Appointment.id, AppointmentRecords.tenant_id == Appointment.tenant_id)",
        foreign_keys = [appointment_id])
    
    employee_id: Mapped[int] = mapped_column(Integer)
    employee: Mapped["Employee"] = relationship(
        primaryjoin="and_(AppointmentRecords.employee_id == Employee.id, AppointmentRecords.tenant_id == Employee.tenant_id)",
        foreign_keys=[employee_id]
    )

    services: Mapped[list[AppointmentServices]] = relationship(
        back_populates = "appointment_record",
        cascade = "all, delete-orphan",
        primaryjoin = "and_(AppointmentRecords.id == AppointmentServices.appointment_record_id, AppointmentRecords.tenant_id == AppointmentServices.tenant_id)",
        foreign_keys = "[AppointmentServices.appointment_record_id]"
    )

    __table_args__ = (
        UniqueConstraint("id", "tenant_id", name = "uq_appointment_record_tenant"),
        ForeignKeyConstraint(
            ["employee_id", "tenant_id"],
            ["employees.id", "employees.tenant_id"],
            ondelete = "RESTRICT",
            name = "fk_appointment_records_employee"
        ),
        ForeignKeyConstraint(
            ["appointment_id", "tenant_id"],
            ["appointments.id", "appointments.tenant_id"],
            ondelete = "CASCADE",
            name = "fk_appointment_records_appointment"
        )
    )

class Appointment(BaseFields):
    __tablename__ = "appointments"

    start_time_est: Mapped[datetime] = mapped_column(DateTime(timezone = True))
    end_time_est: Mapped[datetime] = mapped_column(DateTime(timezone = True))

    client_id: Mapped[int] = mapped_column(Integer)
    client: Mapped["Client"] = relationship(
        primaryjoin = "and_(Appointment.client_id == Client.id, Appointment.tenant_id == Client.tenant_id)",
        foreign_keys = [client_id]
    )
    records: Mapped[list[AppointmentRecords]] = relationship(
        back_populates = "appointment",
        cascade = "all, delete-orphan",
        primaryjoin = "and_(Appointment.id == AppointmentRecords.appointment_id, Appointment.tenant_id == AppointmentRecords.tenant_id)",
        foreign_keys = "[AppointmentRecords.appointment_id]")
    
    receipts: Mapped["Receipt"] = relationship(back_populates = "appointment")

    paid: Mapped[bool] = mapped_column(Boolean, default = False)
    notes: Mapped[str | None] = mapped_column(Text, nullable = True)
    
    status: Mapped[str] = mapped_column(String(50), default = AppointmentStatus.AWAITING)
    cancelled_reason: Mapped[str | None] = mapped_column(String(50), default = None, nullable = True)

    @property
    def total_price(self) -> int:
        return sum(service.price * service.quantity 
                   for record in self.records 
                   for service in record.services)

    __table_args__ = (
        UniqueConstraint("id", "tenant_id", name = "uq_appointment_tenant"),
        UniqueConstraint("client_id", "start_time_est", "end_time_est", name="uq_client_appointment_time"),
        ForeignKeyConstraint(
            ["client_id", "tenant_id"],
            ["clients.id", "clients.tenant_id"],
            ondelete = "CASCADE",
            name = "fk_appoitment_client"
        ),
        CheckConstraint("start_time_est < end_time_est", name="chk_start_before_end")
    )

    ALLOWED_FILTERS = {"client_id", "start_time_est", "end_time_est", "status", "paid", "archived"}