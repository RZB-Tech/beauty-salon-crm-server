from __future__ import annotations
from typing import TYPE_CHECKING
from enum import StrEnum
from datetime import datetime
from sqlalchemy import ForeignKeyConstraint, Index, Integer, String, DateTime, Numeric, Boolean, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.base import BaseFields

if TYPE_CHECKING:
    from src.repository import Service, Material

class PromotionType(StrEnum):
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"

class Promotion(BaseFields):
    __tablename__ = "promotions"

    name: Mapped[str] = mapped_column(String(255))
    promo_type: Mapped[str] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(Text, nullable = True)
    
    service_id: Mapped[int | None] = mapped_column(Integer, nullable = True)
    service: Mapped["Service"] = relationship(
        primaryjoin = "and_(Promotion.service_id == Service.id, Promotion.tenant_id == Service.tenant_id)",
        foreign_keys = [service_id]
    )

    material_id: Mapped[int | None] = mapped_column(Integer, nullable = True)
    material: Mapped["Material"] = relationship(
        primaryjoin = "and_(Promotion.material_id == Material.id, Promotion.tenant_id == Material.tenant_id)",
        foreign_keys = [material_id]
    )

    discount_value: Mapped[int | None] = mapped_column(Numeric, nullable = True) 
    
    start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


    __table_args__ = (
        UniqueConstraint("id", "tenant_id", name="uq_promotion_tenant"),

        Index(
            "uq_promotion_name_tenant_active",
            "name", "tenant_id",
            unique=True,
            postgresql_where=text("is_active = true AND archived = false"),
        ),
        Index(
            "uq_promotion_service_tenant_active",
            "service_id", "tenant_id",
            unique=True,
            postgresql_where=text("is_active = true AND archived = false AND service_id IS NOT NULL"),
        ),
        Index(
            "uq_promotion_material_tenant_active",
            "material_id", "tenant_id",
            unique=True,
            postgresql_where=text("is_active = true AND archived = false AND material_id IS NOT NULL"),
        ),

        ForeignKeyConstraint(
            ["service_id", "tenant_id"],
            ["services.id", "services.tenant_id"],
            ondelete="RESTRICT",
            name="fk_uc_service",
        ),
        ForeignKeyConstraint(
            ["material_id", "tenant_id"],
            ["materials.id", "materials.tenant_id"],
            ondelete="RESTRICT",
            name="fk_uc_material",
        ),
        ForeignKeyConstraint(
            ["created_by_actor_id", "tenant_id"],
            ["actors.id", "actors.tenant_id"],
            ondelete = "SET NULL",
            name = "fk_promotions_created_by_tenant"
        ),
    )

    ALLOWED_FILTERS = {"name", "promo_type", "discount_value", "start_time", "end_time", "is_active", "archived"}