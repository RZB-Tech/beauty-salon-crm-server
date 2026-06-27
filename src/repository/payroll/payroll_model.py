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
    from src.repository.transaction.transaction_model import Transaction

class PayrollEnum(Enum):
    SALARY = "salary"
    ADVANCE_SALARY = "advance salary"
    BONUS = "bonus"
    PENALTY = "penalty"
    COMMISSION = "commission"

class PayoutStatus(Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    CANCELLED = "cancelled"

class Payout(BaseFields):
    __tablename__ = "payouts"

    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id",
                                            ondelete = "CASCADE"))
    amount: Mapped[int] = mapped_column(Integer)
    status: Mapped[PayoutStatus] = mapped_column(SQLEnum(
        PayoutStatus, values_callable = lambda e: [m.value for m in e]
    ), default = PayoutStatus.PENDING)
    notes: Mapped[str | None] = mapped_column(Text, nullable = True)
    payrolls: Mapped[list["Payroll"]] = relationship(back_populates = "payout")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates = "payout")
    cancelled: Mapped[bool] = mapped_column(Boolean, default = False, server_default = "false")

class Payroll(BaseFields):
    __tablename__ = "payrolls"

    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id", ondelete = "CASCADE"))

    amount: Mapped[int] = mapped_column(Integer, default = 0)
    type: Mapped[PayrollEnum] = mapped_column(SQLEnum(
        PayrollEnum, values_callable = lambda e: [m.value for m in e]))
    notes: Mapped[str | None] = mapped_column(Text, nullable = True)

    appointment_id: Mapped[int | None] = mapped_column(ForeignKey("appointments.id"))

    payout_id: Mapped[int | None] = mapped_column(
        ForeignKey("payouts.id", ondelete = "SET NULL"), 
        nullable = True)
    payout: Mapped["Payout"] = relationship(back_populates = "payrolls")

    cancelled: Mapped[bool] = mapped_column(Boolean, default = False, server_default = "false")

    __table_args__ = (
        CheckConstraint("amount >= 1", name = "ck_payorll_amount_non_negative"),
    )

    @validates("amount")
    def validate_amount(self, key, value):
        if value <= 0: raise ValueError("Amount cannot be less than 1")
        return value
    
    ALLOWER_FILTERS = {"employee_id", "amount", "type"}
