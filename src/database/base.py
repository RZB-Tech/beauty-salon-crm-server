from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, func, text
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column, validates
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.mixins import TenantMixin
from src.database.session import get_repository_db

class Base(DeclarativeBase):
    pass



class BaseFields(TenantMixin, Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    archived: Mapped[bool] = mapped_column(Boolean, default = False, server_default = text("false"))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    created_by: Mapped[int | None] = mapped_column(
        ForeignKey("staffs.id", use_alter=True, name="fk_created_by_staff"), 
        nullable = True) 

    @validates("created_by")
    def validate_created_by(self, key, value):
        if self.id is not None and self.created_by is not None:
            if self.created_by != value:
                raise ValueError("Restricted to change creator of object")
        return value
            
    @validates("created_at")
    def validate_created_at(self, key, value):
        if self.id is not None and self.created_at is not None:
            current_val = self.created_at.astimezone() if hasattr(self.created_at, 'astimezone') else self.created_at
            new_val = value.astimezone() if hasattr(value, 'astimezone') else value
            if current_val != new_val:
                raise ValueError("Restricted to change creation date of object")
            
class BaseRepository:
    @property
    def db(self) -> AsyncSession:
        return get_repository_db()