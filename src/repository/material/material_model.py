from __future__ import annotations
from sqlalchemy import (
    ForeignKeyConstraint,
    Index,
    String,
    Integer,Text,
    UniqueConstraint,
    func
)
from sqlalchemy.orm import Mapped, mapped_column
from enum import StrEnum
from src.database.base import BaseFields

class MeasurementUnit(StrEnum):
    PCS = "piece"
    PACK = "pack"
    BOX = "box"
    BOTTLE = "bottle"
    ML = "milliliter"
    L = "liter"
    GR = "gramm"
    KG = "kilogram"

class Material(BaseFields):
    __tablename__ = "materials"
    article: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable = True)

    quantity: Mapped[int] = mapped_column(Integer, default = 0)

    measurement_unit: Mapped[str] = mapped_column(default = MeasurementUnit.PCS)
    volume: Mapped[int] = mapped_column(Integer, default = 0)
    sell_price: Mapped[int] = mapped_column(Integer, default = 0)

    __table_args__ = (
        UniqueConstraint("id", "tenant_id", name = "uq_material_tenant"),
        Index(
            "uq_material_article_lower",
            func.lower(article),
            "tenant_id",
            unique = True
        ),
        ForeignKeyConstraint(
            ["created_by_actor_id", "tenant_id"],
            ["actors.id", "actors.tenant_id"],
            ondelete = "SET NULL (created_by_actor_id)",
            name = "fk_materials_created_by_tenant"
        ),
    )

    ALLOWED_FILTERS = {"article", "name", "measurement_unit", "quantity", "volume", "sell_price", "archived"}
