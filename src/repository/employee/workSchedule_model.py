from __future__ import annotations
from enum import StrEnum
from src.database.base import BaseFields
from sqlalchemy import CheckConstraint, ForeignKeyConstraint, Integer, String, Time, UniqueConstraint
from typing import TYPE_CHECKING
from sqlalchemy import (
    Date,Text
)
from sqlalchemy.orm import Mapped, mapped_column
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
    
    employee_id: Mapped[int] = mapped_column(Integer)

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
        ),
        ForeignKeyConstraint(
            ["created_by_actor_id", "tenant_id"],
            ["actors.id", "actors.tenant_id"],
            ondelete = "SET NULL (created_by_actor_id)",
            name = "fk_employee_absences_created_by_tenant"
        ),
    )

    ALLOWED_FILTERS = {"employee_id", "start_date", "end_date", "absence_type", "archived"}

class WorkSchedule(BaseFields):
    __tablename__ = "employee_work_schedules"

    employee_id: Mapped[int] = mapped_column(Integer)
    
    day_of_week: Mapped[int] = mapped_column(Integer)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)

    __table_args__ = (
        UniqueConstraint("id", "tenant_id", name = "uq_work_schedule_tenant"),
        UniqueConstraint("employee_id", "day_of_week", name="uq_employee_day_of_week"),
        CheckConstraint("day_of_week BETWEEN 1 and 7", name = "chk_valid_day"),
        CheckConstraint("start_time < end_time", name="chk_start_before_end"),
        ForeignKeyConstraint(
            ["employee_id", "tenant_id"],
            ["employees.id", "employees.tenant_id"],
            ondelete = "CASCADE",
            name = "fk_work_schedule_employee_tenant"
        ),
        ForeignKeyConstraint(
            ["created_by_actor_id", "tenant_id"],
            ["actors.id", "actors.tenant_id"],
            ondelete = "SET NULL (created_by_actor_id)",
            name = "fk_employee_work_schedules_created_by_tenant"
        ),
    )

    ALLOWED_FILTERS = {"day", "start_time", "end_time", "archived"}
