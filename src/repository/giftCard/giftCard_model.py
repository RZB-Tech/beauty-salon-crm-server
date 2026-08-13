from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime
from enum import StrEnum
from sqlalchemy import CheckConstraint, DateTime, ForeignKeyConstraint, Index, Integer, String, UniqueConstraint, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.base import BaseFields

if TYPE_CHECKING:
    from src.repository import Client, Receipt

class GiftCardStatus(StrEnum):
    ACTIVE = "active"
    REDEEMED = "redeemed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class GiftCard(BaseFields):
    __tablename__ = "gift_cards"
    code: Mapped[str] = mapped_column(String(50))

    client_id: Mapped[int | None] = mapped_column(Integer, nullable = True)
    client: Mapped["Client"] = relationship(
        primaryjoin = "and_(GiftCard.client_id == Client.id, GiftCard.tenant_id == Client.tenant_id)",
        foreign_keys = [client_id]
    )

    receipt_id: Mapped[int] = mapped_column(Integer)
    receipt: Mapped["Receipt"] = relationship(
        primaryjoin = "and_(GiftCard.receipt_id == Receipt.id, GiftCard.tenant_id == Receipt.tenant_id)",
        foreign_keys = [receipt_id]
    )

    initial_amount: Mapped[int] = mapped_column(Integer)
    remain_amount: Mapped[int] = mapped_column(Integer)

    status: Mapped[str] = mapped_column(String(50), default = GiftCardStatus.ACTIVE)
    issue_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expiration_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable = True)

    __table_args__ = (
        UniqueConstraint("id", "tenant_id", name = "uq_gift_card_tenant"),
        CheckConstraint("initial_amount >= 1", "cc_initial_amount_positive"),
        Index(
            "uq_gift_card_code",
            func.lower(code),
            unique = True
        ),
        ForeignKeyConstraint(
            ["client_id", "tenant_id"],
            ["clients.id", "clients.tenant_id"],
            ondelete = "CASCADE",
            name = "fk_gift_card_client"
        ),
        ForeignKeyConstraint(
            ["receipt_id", "tenant_id"],
            ["receipts.id", "receipts.tenant_id"],
            ondelete = "RESTRICT",
            name = "fk_gift_card_receipt"
        )
    )

    ALLOWED_FILTERS = {"code", "client_id", "initial_amount", "remain_amount", "status", "issue_date", "expiraton_date"}
