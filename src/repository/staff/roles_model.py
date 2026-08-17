from __future__ import annotations
from sqlalchemy import ForeignKeyConstraint, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ARRAY
from src.database.base import BaseFields

class Role(BaseFields):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable = True)
    permissions: Mapped[list[int]] = mapped_column(ARRAY(Integer), default = list, server_default = "{}")

    __table_args__ = (
        UniqueConstraint("id", "tenant_id", name = "uq_roles_tenant"),
        ForeignKeyConstraint(
            ["created_by_actor_id", "tenant_id"],
            ["actors.id", "actors.tenant_id"],
            ondelete = "SET NULL",
            name = "fk_roles_created_by_tenant"
        ),
    )

    ALLOWED_FILTERS = {"name", "archived"}