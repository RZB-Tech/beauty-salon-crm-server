from enum import Enum

from sqlalchemy import ForeignKeyConstraint, Integer, String, Boolean, Enum as SQLEnum, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, validates

from src.database.base import BaseFields

class StaffType(Enum):
    ADMIN = "administrator"
    EMPLOYEE = "employee"
    TELEGRAM_BOT = "telegram bot"

class Staff(BaseFields):
    __tablename__ = "staffs"

    firstname: Mapped[str] = mapped_column(String(255))
    lastname: Mapped[str | None] = mapped_column(String(255), nullable=True)
    middlename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    login: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    staff_type: Mapped[StaffType] = mapped_column(SQLEnum(
        StaffType, values_callable = lambda e: [m.value for m in e]))
    
    employee_id: Mapped[int | None] = mapped_column(Integer, nullable = True)
    
    __table_args__ = (
        UniqueConstraint("id", "tenant_id", name = "uq_staff_tenant"),
        ForeignKeyConstraint(
            ["employee_id", "tenant_id"],
            ["employees.id", "employees.tenant_id"],
            ondelete = "SET NULL (employee_id)",
            name = "fk_staff_employee"
        ),
    )
 
    @validates("login")
    def validate_login_lowercase(self, key: str, value: str) -> str:
        if value is not None: return value.strip().lower()
        return value