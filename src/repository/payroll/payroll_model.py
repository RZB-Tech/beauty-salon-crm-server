from enum import Enum
from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Enum as SQLEnum,
    Integer,
    Text
)
from sqlalchemy.orm import Mapped, mapped_column, validates
from src.database.base import BaseFields

class PayrollEnum(Enum):
    SALARY = "salary"
    BONUS = "bonus"
    PENALTY = "penalty"
    COMMISSION = "commission"

class Payroll(BaseFields):
    __tablename__ = "payrolls"

    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id", ondelete = "CASCADE"))
    amount: Mapped[int] = mapped_column(Integer, default = 0)
    type: Mapped[PayrollEnum] = mapped_column(SQLEnum(
        PayrollEnum, values_callable = lambda e: [m.value for m in e]))
    notes: Mapped[str | None] = mapped_column(Text, nullable = True)

    appointment_id: Mapped[int | None] = mapped_column(ForeignKey("appointments.id"))

    __table_args__ = (
        CheckConstraint("amount >= 1", name = "ck_payorll_amount_non_negative"),
    )

    @validates("amount")
    def validate_amount(self, key, value):
        if value <= 0: raise ValueError("Amount cannot be less than 1")
        return value
    
    ALLOWER_FILTERS = {"employee_id", "amount", "type"}