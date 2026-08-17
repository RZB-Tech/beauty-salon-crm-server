from __future__ import annotations
from sqlalchemy import ForeignKeyConstraint, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from src.database.base import BaseFields

class StaffRole(BaseFields):
    __tablename__ = "staffs_roles"

    staff_id: Mapped[int] = mapped_column(Integer)
    role_id: Mapped[int] = mapped_column(Integer)

    __table_args__ = (
        UniqueConstraint("staff_id", "role_id", name = "pk_staffs_roles"),
        ForeignKeyConstraint(
            ["staff_id", "tenant_id"],
            ["staffs.id", "staffs.tenant_id"],
            ondelete = "CASCADE",
            name = "fk_staffs_roles_to_staff"
        ),
        ForeignKeyConstraint(
            ["role_id", "tenant_id"],
            ["roles.id", "roles.tenant_id"],
            ondelete = "CASCADE",
            name = "fk_staffs_roles_to_role"
        ),
        ForeignKeyConstraint(
            ["created_by_actor_id", "tenant_id"],
            ["actors.id", "actors.tenant_id"],
            ondelete = "SET NULL (created_by_actor_id)",
            name = "fk_staffs_roles_created_by_tenant"
        ),
    )