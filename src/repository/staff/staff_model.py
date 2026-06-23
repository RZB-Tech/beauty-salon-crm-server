from enum import Enum

from sqlalchemy import ForeignKey, String, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, validates

from src.database.base import BaseFields
from src.database.mixins import TenantMixin

class StaffType(Enum):
    SUPER_ADMIN = "super administrator"
    ADMIN = "administrator"
    EMPLOYEE = "employee"

class Staff(TenantMixin, BaseFields):
    __tablename__ = "staffs"

    firstname: Mapped[str] = mapped_column(String(255))
    lastname: Mapped[str | None] = mapped_column(String(255), nullable=True)
    middlename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    login: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    staff_type: Mapped[StaffType] = mapped_column(SQLEnum(
        StaffType, values_callable = lambda e: [m.value for m in e]))
    
    employee_id: Mapped[int | None] = mapped_column(ForeignKey("employees.id", ondelete = "SET NULL"), nullable = True)
 
    @validates("login")
    def validate_login_lowercase(self, key: str, value: str) -> str:
        if value is not None: return value.strip().lower()
        return value