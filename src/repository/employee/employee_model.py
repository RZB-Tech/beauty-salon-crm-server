from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import (
    ForeignKeyConstraint,
    Index,
    String,
    ForeignKey,
    Boolean,
    BigInteger,
    Integer,
    Date,
    UniqueConstraint,
    func, Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date

from src.database.base import BaseFields

if TYPE_CHECKING:
    from src.repository.service.service_model import Service

class Specialization(BaseFields):
    __tablename__ = "specializations"
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    __table_args__ = (
        Index(
            "uq_specialization_name_lower", 
            func.lower(name),
            "tenant_id",
            unique=True
        ),
        UniqueConstraint("id", "tenant_id", name="uq_specialization_id_tenant"),
    )

    employees: Mapped[list["Employee"]] = relationship(
        back_populates="specialization"
    )

    ALLOWED_FILTERS = {"name", "archived"}

class Employee(BaseFields):
    __tablename__ = "employees"

    firstname: Mapped[str] = mapped_column(String(255))
    lastname: Mapped[str | None] = mapped_column(String(255), nullable=True)
    middlename: Mapped[str | None] = mapped_column(String(255), nullable=True)

    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    birth_date: Mapped[date] = mapped_column(Date)

    active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    specialization_id: Mapped[int | None] = mapped_column(Integer, nullable = True)
    specialization: Mapped["Specialization"] = relationship(
        back_populates="employees"
    )

    services: Mapped[list["Service"]] = relationship(
        secondary="employee_services",
        back_populates="employees",
    )

    salary_fixed: Mapped[int] = mapped_column(BigInteger, default=0)
    percent_from_services: Mapped[int] = mapped_column(Integer, default=0)
    percent_from_sales: Mapped[int] = mapped_column(Integer, default=0)

    notes: Mapped[str | None] = mapped_column(Text, nullable = True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["specialization_id", "tenant_id"],
            ["specializations.id", "specializations.tenant_id"],
            ondelete="SET NULL",
            name="fk_employee_specialization_tenant"
        ),
    )

    ALLOWED_FILTERS = {"firstname", "lastname", "middlename", "phone", "active", "specialization_id", "archived"}