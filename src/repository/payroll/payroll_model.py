from __future__ import annotations
from enum import StrEnum
from typing import TYPE_CHECKING
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from src.database.base import BaseFields

if TYPE_CHECKING: 
    from src.repository.transaction.transaction_model import Transaction

class PayrollType(StrEnum):
    BONUS = "bonus"
    PENALTY = "penalty"
    COMMISSION = "commission"

class PayrollStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"

class PayoutType(StrEnum):
    SALARY = "salary"
    ADVANCE_SALARY = "advance salary"
    OTHER = "other"

class PayoutMethod(StrEnum):
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
    type: Mapped[str] = mapped_column(String(50))
    method: Mapped[str] = mapped_column(String(50))
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
        ForeignKeyConstraint(
            ["created_by_actor_id", "tenant_id"],
            ["actors.id", "actors.tenant_id"],
            ondelete = "SET NULL",
            name = "fk_payouts_created_by_tenant"
        ),
        Index("ix_payouts_tenant_employee", "tenant_id", "employee_id"),
    )
    
    ALLOWED_FILTERS = {"employee_id", "type", "method", "cancelled", "archived"}

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
    notes: Mapped[str | None] = mapped_column(Text, nullable = True)
    auto_generated: Mapped[bool] = mapped_column(Boolean, default = False, server_default = "false")

    type: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default = PayrollStatus.PENDING)

    __table_args__ = (
        UniqueConstraint("id", "tenant_id", name = "uq_payroll_tenant"),
        CheckConstraint("amount >= 1", name = "ck_payorll_amount_non_negative"),
        ForeignKeyConstraint(
            ["employee_id", "tenant_id"],
            ["employees.id", "employees.tenant_id"],
            ondelete = "CASCADE",
            name = "fk_payroll_employee"
        ),
        Index("ix_payrolls_tenant_employee", "tenant_id", "employee_id"),
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
        ),
        ForeignKeyConstraint(
            ["created_by_actor_id", "tenant_id"],
            ["actors.id", "actors.tenant_id"],
            ondelete = "SET NULL",
            name = "fk_payrolls_created_by_tenant"
        )
    )

    @validates("amount")
    def validate_amount(self, key, value):
        if value <= 0: raise ValueError("Сумма не может быть меньше 1")
        return value
    
    ALLOWED_FILTERS = {"amount", "employee_id", "amount", "type", "status", "auto_generated", "archived"}
