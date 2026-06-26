from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Enum as SQLEnum,
    Integer,
    Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from src.database.base import BaseFields

if TYPE_CHECKING: 
    from src.repository.payroll.payroll_model import Payout

class TransactionType(Enum):
    INCOME = "income"
    EXPENSE = "expense"

class TransactionCategory(Enum):
    APPOINTMENT = "appointment"
    DIRECT_SALE = "direct sale"
    SALARY = "salary"
    ADVANCE_SALARY = "salary"
    UTILITY = "utility"
    INTERNET = "internet"
    TELEPHONE = "telephone"
    OTHER = "other"

class TransactionMethod(Enum):
    CARD = "card"
    CASH = "cash"
    BANK_TRANSER = "bank transfer"
    DEPOSIT = "deposit"

class Transaction(BaseFields):
    __tablename__ = "transactions"

    amount: Mapped[int] = mapped_column(Integer)
    type: Mapped[TransactionType] = mapped_column(
        SQLEnum(TransactionType, values_callable = lambda e: [m.value for m in e]))
    method: Mapped[TransactionMethod] = mapped_column(
        SQLEnum(TransactionMethod, values_callable = lambda e: [m.value for m in e]))
    category: Mapped[TransactionCategory] = mapped_column(
        SQLEnum(TransactionCategory, values_callable = lambda e: [m.value for m in e]))
    receipt_id: Mapped[int | None] = mapped_column(
        ForeignKey("receipts.id", ondelete = "RESTRICT"))
    
    payout_id: Mapped[int | None] = mapped_column(
        ForeignKey("payouts.id", ondelete = "RESTRICT"))
    payout: Mapped["Payout"] = relationship(back_populates = "transactions")
    
    notes: Mapped[str | None] = mapped_column(Text, nullable = True)

    auto_generated: Mapped[bool] = mapped_column(Boolean, default = False, server_default = "false")
 