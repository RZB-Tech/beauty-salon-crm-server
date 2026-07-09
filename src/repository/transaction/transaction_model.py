from __future__ import annotations
from enum import StrEnum
from typing import TYPE_CHECKING
from sqlalchemy import (
    Boolean,
    Enum as SQLEnum,
    ForeignKeyConstraint,
    Integer,
    String,
    Text,
    UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.base import BaseFields

if TYPE_CHECKING: 
    from src.repository.payroll.payroll_model import Payout

class TransactionType(StrEnum):
    INCOME = "income"
    EXPENSE = "expense"

class TransactionCategory(StrEnum):
    RECEIPT = "receipt"
    EMPLOYEE_PAYMENT = "employee payment"
    UTILITY = "utility"
    INTERNET = "internet"
    TELEPHONE = "telephone"
    OTHER = "other"

class TransactionMethod(StrEnum):
    CARD = "card"
    CASH = "cash"
    BANK_TRANSER = "bank transfer"
    DEPOSIT = "deposit"

class Transaction(BaseFields):
    __tablename__ = "transactions"

    amount: Mapped[int] = mapped_column(Integer)
    type: Mapped[str] = mapped_column(String(50))
    method: Mapped[str] = mapped_column(String(50))
    category: Mapped[str] = mapped_column(String(50))
    
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