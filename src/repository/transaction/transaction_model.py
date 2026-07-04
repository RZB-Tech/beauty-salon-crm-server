from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING
from sqlalchemy import (
    Boolean,
    ForeignKey,
    Enum as SQLEnum,
    ForeignKeyConstraint,
    Integer,
    Text,
    UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.base import BaseFields

if TYPE_CHECKING: 
    from src.repository.payroll.payroll_model import Payout

class TransactionType(Enum):
    INCOME = "income"
    EXPENSE = "expense"

class TransactionCategory(Enum):
    RECEIPT = "receipt"
    EMPLOYEE_PAYMENT = "employee payment"
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
    
    notes: Mapped[str | None] = mapped_column(Text, nullable = True)
    cancelled: Mapped[bool] = mapped_column(Boolean, default = False, server_default = "false")
    auto_generated: Mapped[bool] = mapped_column(Boolean, default = False, server_default = "false")

    receipt_id: Mapped[int | None] = mapped_column(Integer, nullable = True)
    payout_id: Mapped[int | None] = mapped_column(Integer, nullable = True)
    payout: Mapped["Payout"] = relationship(
        back_populates = "transactions",
        primaryjoin = "and_(Transaction.payout_id == Payout.id, Transaction.tenant_id == Payout.tenant_id)",
        foreign_keys = [payout_id])

    __table_args__ = (
        UniqueConstraint("id", "tenant_id", name = "uq_transaction_tenant"),
        ForeignKeyConstraint(
            ["receipt_id", "tenant_id"],
            ["receipts.id", "receipts.tenant_id"],
            ondelete = "SET NULL (receipt_id)",
            name = "fk_transcation_receipt"
        ),
        ForeignKeyConstraint(
            ["payout_id", "tenant_id"],
            ["payouts.id", "payouts.tenant_id"],
            ondelete = "SET NULL (payout_id)",
            name = "fk_transcation_payout"
        ),
    )
 
    ALLOWED_FILTERS = {"amount", "type", "method", "category", "cancelled", "auto_generated", "archived"}