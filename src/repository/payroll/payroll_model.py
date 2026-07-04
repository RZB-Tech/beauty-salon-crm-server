from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Enum as SQLEnum,
    ForeignKeyConstraint,
    Integer,
    Text,
    UniqueConstraint
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

    employee_id: Mapped[int] = mapped_column(Integer)
    payrolls: Mapped[list["Payroll"]] = relationship(
        back_populates = "payout",
        primaryjoin = "and_(Payout.id == Payroll.payout_id, Payout.tenant_id == Payroll.tenant_id)",
        foreign_keys = "[Payroll.payout_id]")
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates = "payout",
        primaryjoin = "and_(Payout.id == Transaction.payout_id, Payout.tenant_id == Transaction.tenant_id)",
        foreign_keys = "[Transaction.payout_id]")

    amount: Mapped[int | None] = mapped_column(Integer, nullable = True)
    type: Mapped[PayoutType] = mapped_column(SQLEnum(
        PayoutType, values_callable = lambda e: [m.value for m in e]
    ))
    method: Mapped[PayoutType] = mapped_column(SQLEnum(
        PayoutMethod, values_callable = lambda e: [m.value for m in e]
    ))
    notes: Mapped[str | None] = mapped_column(Text, nullable = True)
    cancelled: Mapped[bool] = mapped_column(Boolean, default = False, server_default = "false")

    @property
    def total_amount(self) -> int:
        if not self.payrolls: return 0
        total = 0
        for payroll in self.payrolls:
            if payroll.type == PayrollType.PENALTY:
                total -= payroll.amount
            else: total += payroll.amount
        if self.amount: total += self.amount
        return total
    
    __table_args__ = (
        UniqueConstraint("id", "tenant_id", name = "uq_payout_tenant"),
        ForeignKeyConstraint(
            ["employee_id", "tenant_id"],
            ["employees.id", "employees.tenant_id"],
            ondelete = "CASCADE",
            name = "fk_payout_employee"
        ),
    )
    
    ALLOWER_FILTERS = {"employee_id", "type", "method", "cancelled", "archived"}

class Payroll(BaseFields):
    __tablename__ = "payrolls"

    employee_id: Mapped[int] = mapped_column(Integer)
    payout_id: Mapped[int | None] = mapped_column(Integer, nullable = True)
    payout: Mapped["Payout"] = relationship(
        back_populates = "payrolls",
        primaryjoin = "and_(Payroll.payout_id == Payout.id, Payroll.tenant_id == Payout.tenant_id)",
        foreign_keys = [payout_id])
    appointment_id: Mapped[int | None] = mapped_column(Integer, nullable = True)

    amount: Mapped[int] = mapped_column(Integer, default = 0)
    type: Mapped[PayrollType] = mapped_column(SQLEnum(
        PayrollType, values_callable = lambda e: [m.value for m in e]))
    notes: Mapped[str | None] = mapped_column(Text, nullable = True)

    status: Mapped[PayrollStatus] = mapped_column(SQLEnum(
        PayrollStatus, values_callable = lambda e: [m.value for m in e]), default = PayrollStatus.PENDING)
    auto_genereted: Mapped[bool] = mapped_column(Boolean, default = False, server_default = "false")

    __table_args__ = (
        UniqueConstraint("id", "tenant_id", name = "uq_payroll_tenant"),
        CheckConstraint("amount >= 1", name = "ck_payorll_amount_non_negative"),
        ForeignKeyConstraint(
            ["employee_id", "tenant_id"],
            ["employees.id", "employees.tenant_id"],
            ondelete = "CASCADE",
            name = "fk_payroll_employee"
        ),
        ForeignKeyConstraint(
            ["payout_id", "tenant_id"],
            ["payouts.id", "payouts.tenant_id"],
            ondelete = "CASCADE",
            name = "fk_payroll_payout"
        ),
        ForeignKeyConstraint(
            ["appointment_id", "tenant_id"],
            ["appointments.id", "appointments.tenant_id"],
            ondelete = "CASCADE",
            name = "fk_payroll_appointment"
        )
    )

    @validates("amount")
    def validate_amount(self, key, value):
        if value <= 0: raise ValueError("Amount cannot be less than 1")
        return value
    
    ALLOWER_FILTERS = {"amount", "employee_id", "amount", "type", "status", "auto_generated", "archived"}
