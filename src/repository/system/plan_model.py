from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import (
    Boolean,
    String,
    Integer,
    Text
)
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base

class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    name: Mapped[str] = mapped_column(String(255), unique = True)
    description: Mapped[str] = mapped_column(Text, nullable = True)

    price: Mapped[int] = mapped_column(Integer)

    max_employee: Mapped[int] = mapped_column(Integer)
    max_clients: Mapped[int] = mapped_column(Integer)
    max_services: Mapped[int] = mapped_column(Integer)
    max_materials: Mapped[int] = mapped_column(Integer)
    max_archive_period: Mapped[int] = mapped_column(Integer) # in months

    is_visible: Mapped[bool] = mapped_column(Boolean, default = False)