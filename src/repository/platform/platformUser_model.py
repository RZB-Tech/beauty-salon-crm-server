from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, validates
from src.database.base import Base

class PlatformUser(Base):
    __tablename__ = "platform_users"

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    login: Mapped[str] = mapped_column(String(100), unique = True, index = True)
    hashed_password: Mapped[str] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, default = True, server_default = "true")

    @validates("login")
    def validate_login_lowercase(self, key: str, value: str) -> str:
        return value.strip().lower()
