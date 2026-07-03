from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import (
    Index,
    String,
    Boolean,
    Integer,Text,
    func
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum as SQLEnum
from enum import Enum
from src.database.base import BaseFields

class MeasurementUnit(Enum):
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

    measurement_unit: Mapped[MeasurementUnit] = mapped_column(SQLEnum(
        MeasurementUnit, values_callable = lambda e: [m.value for m in e]), 
        default = MeasurementUnit.PCS)
    volume: Mapped[int] = mapped_column(Integer, default = 0)
    sell_price: Mapped[int] = mapped_column(Integer, default = 0)

    __table_args__ = (
        Index(
            "uq_article_name_lower", 
            func.lower(article),
            "tenant_id",
            unique=True
        ),
    )

    ALLOWED_FILTERS = {"article", "name", "measurement_unit", "quantity", "volume", "sell_price", "archived"}
