from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING
from sqlalchemy import (
    String,
    Integer,
    Date,
    Text
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date
from src.database.base import BaseFields

class Sex(Enum):
    MALE = "male"
    FEMALE = "female"

class Client(BaseFields):
    __tablename__ = "clients"

    firstname: Mapped[str] = mapped_column(String(255))
    lastname: Mapped[str | None] = mapped_column(String(255), nullable=True)
    middlename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable = True)
    sex: Mapped[Sex] = mapped_column(SQLEnum(Sex, values_callable = lambda e: [m.value for m in e]))
    notes: Mapped[str | None] = mapped_column(Text, nullable = True)
    deposit: Mapped[int] = mapped_column(Integer, default = 0)

    ALLOWED_FILTERS = {"firstname", "lastname", "middlename", "phone", "birth_data", "sex"}