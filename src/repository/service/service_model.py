from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import (
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    ForeignKey,
    BigInteger,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.base import BaseFields

if TYPE_CHECKING:
    from src.repository.employee.employee_model import Employee

class ServiceCategory(BaseFields):
    __tablename__ = "service_categories"
    name: Mapped[str] = mapped_column(String(255))

    services: Mapped[list["Service"]] = relationship(
        back_populates="category"
    )

    __table_args__ = (
        Index(
            "uq_service_category_name_lower", 
            func.lower(name),
            "tenant_id",
            unique=True
        ),
        UniqueConstraint("id", "tenant_id", name="uq_service_category_id_tenant")
    )

    ALLOWED_FILTERS = {"name", "archived"}

class Service(BaseFields):
    __tablename__ = "services"

    name: Mapped[str] = mapped_column(String(255))
    price: Mapped[int] = mapped_column(BigInteger, default=0)
    
    category_id: Mapped[int | None] = mapped_column(Integer, nullable = True)
    category: Mapped["ServiceCategory"] = relationship(
        back_populates="services"
    )

    employees: Mapped[list["Employee"]] = relationship(
        secondary="employee_services",
        back_populates="services",
    )

    __table_args__ = (
        Index(
            "uq_service_name_lower", 
            func.lower(name),
            "tenant_id",
            unique=True
        ),
        ForeignKeyConstraint(
            ["category_id", "tenant_id"],
            ["service_categories.id", "service_categories.tenant_id"],
            ondelete="RESTRICT",
            name="fk_service_category_tenant"
        ),
    )

    ALLOWED_FILTERS = {"name", "price", "category_id", "archived"}