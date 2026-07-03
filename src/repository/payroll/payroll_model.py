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

class PayrollType(Enum):
    BONUS = "bonus"
    PENALTY = "penalty"
    COMMISSION = "commission"

class PayrollStatus(Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"

class PayoutType(Enum):
    SALARY = "salary"
    ADVANCE_SALARY = "advance salary"
    OTHER = "other"

class PayoutMethod(Enum):
    CASH = "cash"
    CARD = "card"

class Payout(BaseFields):
    __tablename__ = "payouts"

    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id",
                                            ondelete = "CASCADE"))
    type: Mapped[PayoutType] = mapped_column(SQLEnum(
        PayoutType, values_callable = lambda e: [m.value for m in e]
    ))
    method: Mapped[PayoutType] = mapped_column(SQLEnum(
        PayoutMethod, values_callable = lambda e: [m.value for m in e]
    ))
    notes: Mapped[str | None] = mapped_column(Text, nullable = True)
    payrolls: Mapped[list["Payroll"]] = relationship(back_populates = "payout")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates = "payout")
    cancelled: Mapped[bool] = mapped_column(Boolean, default = False, server_default = "false")

    @property
    def total_amount(self) -> int:
        if not self.payrolls: return 0
        total = 0
        for payroll in self.payrolls:
            if payroll.type == PayrollType.PENALTY:
                total -= payroll.amount
            else: total += payroll.amount
        return total
    
    ALLOWER_FILTERS = {"employee_id", "type", "method", "cancelled", "archived"}

class Payroll(BaseFields):
    __tablename__ = "payrolls"

    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id", ondelete = "CASCADE"))

    amount: Mapped[int] = mapped_column(Integer, default = 0)
    type: Mapped[PayrollType] = mapped_column(SQLEnum(
        PayrollType, values_callable = lambda e: [m.value for m in e]))
    notes: Mapped[str | None] = mapped_column(Text, nullable = True)

    appointment_id: Mapped[int | None] = mapped_column(ForeignKey("appointments.id"))

    payout_id: Mapped[int | None] = mapped_column(
        ForeignKey("payouts.id", ondelete = "SET NULL"), 
        nullable = True)
    payout: Mapped["Payout"] = relationship(back_populates = "payrolls")
    status: Mapped[PayrollStatus] = mapped_column(SQLEnum(
        PayrollStatus, values_callable = lambda e: [m.value for m in e]), default = PayrollStatus.PENDING)
    auto_genereted: Mapped[bool] = mapped_column(Boolean, default = False, server_default = "false")

    __table_args__ = (
        CheckConstraint("amount >= 1", name = "ck_payorll_amount_non_negative"),
    )

    @validates("amount")
    def validate_amount(self, key, value):
        if value <= 0: raise ValueError("Amount cannot be less than 1")
        return value
    
    ALLOWER_FILTERS = {"amount", "employee_id", "amount", "type", "status", "auto_generated", "archived"}
