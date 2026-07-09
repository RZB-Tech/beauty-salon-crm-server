from __future__ import annotations
from enum import Enum, StrEnum
from src.database.base import BaseFields
from sqlalchemy import CheckConstraint, Enum as SQLEnum, ForeignKeyConstraint, Integer, String, Time, UniqueConstraint
from typing import TYPE_CHECKING
from sqlalchemy import (
    ForeignKey,
    Date,Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, time

if TYPE_CHECKING:
    from src.repository.employee.employee_model import Employee

class AbsenceEnum(StrEnum):
    SICK = "sick"
    VACATION = "vacation"
    DAY_OFF = "day off"
    WEEKEND = "weekend"
    OTHER = "other"

class EmployeeAbsence(BaseFields):
    __tablename__ = "employee_absences"
    
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id", ondelete = "CASCADE"))

    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)

    absence_type: Mapped[str] = mapped_column(String(50))
    reason: Mapped[str | None] = mapped_column(Text, nullable = True)

    __table_args__ = (
        UniqueConstraint("id", "tenant_id", name = "uq_employee_absence_tenant"),
        UniqueConstraint("employee_id", "start_date", "end_date", "tenant_id", name="uq_employee_absence_days"),
        CheckConstraint("start_date < end_date", name="chk_start_before_end"),
        ForeignKeyConstraint(
            ["employee_id", "tenant_id"],
            ["employees.id", "employees.tenant_id"],
            ondelete = "CASCADE",
            name = "fk_employee_absence_tenant"
        )
    )

    ALLOWED_FILTERS = {"employee_id", "start_date", "end_date", "absence_type", "archived"}

class WorkSchedule(BaseFields):
    __tablename__ = "employee_work_schedules"

    employee_id: Mapped[int] = mapped_column(Integer)
    
    day: Mapped[date] = mapped_column(Date)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)

    __table_args__ = (
        UniqueConstraint("id", "tenant_id", name = "uq_work_schedule_tenant"),
        UniqueConstraint("employee_id", "day", name="uq_employee_day_of_week"),
        CheckConstraint("start_time < end_time", name="chk_start_before_end"),
        ForeignKeyConstraint(
            ["employee_id", "tenant_id"],
            ["employees.id", "employees.tenant_id"],
            ondelete = "CASCADE",
            name = "fk_work_schedule_employee_tenant"
        )
    )

    ALLOWED_FILTERS = {"day", "start_time", "end_time", "archived"}
