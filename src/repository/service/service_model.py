from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import (
    String,
    ForeignKey,
    BigInteger,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.base import BaseFields
from src.database.mixins import TenantMixin

if TYPE_CHECKING:
    from src.repository.employee.employee_model import Employee
    from src.repository.appointment.appointment_model import AppointmentServices

class ServiceCategory(TenantMixin, BaseFields):
    __tablename__ = "service_categories"
    # name: Mapped[str] = mapped_column(String(255), unique=True)
    name: Mapped[str] = mapped_column(String(255))

    services: Mapped[list["Service"]] = relationship(
        back_populates="category"
    )

    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_tenant_service_category_name"),
    )

    ALLOWED_FILTERS = {"name"}

class Service(BaseFields):
    __tablename__ = "services"

    name: Mapped[str] = mapped_column(String(255), unique=True)
    price: Mapped[int] = mapped_column(BigInteger, default=0)

    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("service_categories.id"),
        nullable=True,
    )

    category: Mapped["ServiceCategory"] = relationship(
        back_populates="services"
    )

    employees: Mapped[list["Employee"]] = relationship(
        secondary="employee_services",
        back_populates="services",
    )

    ALLOWED_FILTERS = {"name", "price", "category_id"}