from __future__ import annotations
from datetime import date, datetime
from sqlalchemy import BigInteger, Date, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column
from src.database.base import Base

class GlobalClient(Base):
    """
    Platform-level client profile for the Telegram mini app - not tenant-scoped,
    so a client fills their data once and can request appointments at any tenant.
    A row exists only once the client has registered (POST /mini-app/me), so every
    required field is always set. Linked to a tenant's own Client row via
    Client.global_client_id (and Client.telegram_user_id) once a tenant confirms
    their first request.
    """
    __tablename__ = "global_clients"

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    telegram_user_id: Mapped[int] = mapped_column(BigInteger, unique = True, index = True)
    telegram_username: Mapped[str | None] = mapped_column(String(255), nullable = True)

    # Verified: only ever set from Telegram's signed contact sharing, never typed by the client
    telegram_phone: Mapped[str] = mapped_column(String(50), unique = True)
    # Unverified: typed by the client, number to call if it differs from the Telegram one.
    # Staff choose which of the two a tenant's new Client gets when confirming.
    call_phone: Mapped[str | None] = mapped_column(String(50), nullable = True)

    firstname: Mapped[str] = mapped_column(String(255))
    lastname: Mapped[str] = mapped_column(String(255))
    middlename: Mapped[str | None] = mapped_column(String(255), nullable = True)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable = True)
    sex: Mapped[str] = mapped_column(String(50))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone = True),
        server_default = func.now(),
        nullable = False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone = True),
        server_default = func.now(),
        onupdate = func.now(),
        nullable = False,
    )

