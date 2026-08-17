from __future__ import annotations
from enum import StrEnum
from typing import TYPE_CHECKING
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.base import BaseFields

if TYPE_CHECKING: 
    from src.repository.appointment.appointment_model import Appointment, AppointmentServices
    from src.repository.material.material_model import Material
    from src.repository.transaction.transaction_model import Transaction
    from src.repository.giftCard.giftCard_model import GiftCard

class ReceiptStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"

class ReceiptType(StrEnum):
    APPOINTMENT = "appointment"
    DIRECT_SALE = "direct sale"

class ReceiptItem(BaseFields):
    __tablename__ = "receipt_items"
    receipt_id: Mapped[int] = mapped_column(Integer)
    material_id: Mapped[int | None] = mapped_column(Integer, nullable = True)
    giftCard_id: Mapped[int | None] = mapped_column(Integer, nullable = True)
    appointment_service_id: Mapped[int | None] = mapped_column(Integer, nullable = True)

    receipt: Mapped["Receipt"] = relationship(
        back_populates = "items",
        primaryjoin = "and_(ReceiptItem.receipt_id == Receipt.id, ReceiptItem.tenant_id == Receipt.tenant_id)",
        foreign_keys = [receipt_id])
    material: Mapped["Material"] = relationship(
        primaryjoin = "and_(ReceiptItem.material_id == Material.id, ReceiptItem.tenant_id == Material.tenant_id)",
        foreign_keys = [material_id]
    )
    appointment_service: Mapped["AppointmentServices"] = relationship(
        primaryjoin = "and_(ReceiptItem.appointment_service_id == AppointmentServices.id, ReceiptItem.tenant_id == AppointmentServices.tenant_id)",
        foreign_keys = [appointment_service_id]
    )
    giftCard: Mapped["GiftCard"] = relationship(
        primaryjoin = "and_(ReceiptItem.giftCard_id == GiftCard.id, ReceiptItem.tenant_id == GiftCard.tenant_id)",
        foreign_keys = [giftCard_id]
    )

    base_price: Mapped[int] = mapped_column(Integer)
    final_price: Mapped[int] = mapped_column(Integer)
    quantity: Mapped[int] = mapped_column(Integer, default = 1)

    notes: Mapped[str | None] = mapped_column(Text, nullable = True)

    __table_args__ = (
        UniqueConstraint("id", "tenant_id", name = "uq_receipt_item_tenant"),
        CheckConstraint(
            "(material_id IS NOT NULL AND appointment_service_id IS NULL AND giftCard_id IS NULL) OR "
            "(material_id IS NULL AND appointment_service_id IS NOT NULL AND giftCard_id IS NULL) OR "
            "(material_id IS NULL AND appointment_service_id IS NULL AND giftCard_id IS NOT NULL)",
            name="chk_receipt_item_exclusive_source"
        ),
        ForeignKeyConstraint(
            ["receipt_id", "tenant_id"],
            ["receipts.id", "receipts.tenant_id"],
            ondelete = "CASCADE",
            name = "fk_receipt_items_receipt"
        ),
        ForeignKeyConstraint(
            ["material_id", "tenant_id"],
            ["materials.id", "materials.tenant_id"],
            ondelete = "RESTRICT",
            name = "fk_material_items_receipt"
        ),
        ForeignKeyConstraint(
            ["appointment_service_id", "tenant_id"],
            ["appointment_services.id", "appointment_services.tenant_id"],
            ondelete = "CASCADE",
            name = "fk_appointment_service_item_receipt"
        ),
        ForeignKeyConstraint(
            ["created_by_actor_id", "tenant_id"],
            ["actors.id", "actors.tenant_id"],
            ondelete = "SET NULL",
            name = "fk_receipt_items_created_by_tenant"
        )
    )

    @property
    def discount_amount(self) -> int:
        return self.final_price - self.base_price
    
    @property
    def total_price(self) -> int:
        return self.final_price * self.quantity

class Receipt(BaseFields):
    __tablename__ = "receipts"

    appointment_id: Mapped[int | None] = mapped_column(Integer, nullable = True)
    appointment: Mapped["Appointment"] = relationship(
        back_populates = "receipts",
        primaryjoin = "and_(Receipt.appointment_id == Appointment.id, Receipt.tenant_id == Appointment.tenant_id)",
        foreign_keys = [appointment_id])
    
    client_id: Mapped[int | None] = mapped_column(Integer, nullable = True)

    items: Mapped[list[ReceiptItem]] = relationship(
        back_populates = "receipt", 
        cascade = "all, delete-orphan",
        primaryjoin = "and_(Receipt.id == ReceiptItem.receipt_id, Receipt.tenant_id == ReceiptItem.tenant_id)",
        foreign_keys = "[ReceiptItem.receipt_id]")

    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates = "receipt",
        primaryjoin = "and_(Receipt.id == Transaction.receipt_id, Receipt.tenant_id == Transaction.tenant_id)",
        foreign_keys = "[Transaction.receipt_id]",
        lazy = "raise")
    
    receipt_type: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default = ReceiptStatus.PENDING)

    subtotal_amount: Mapped[int] = mapped_column(Integer, default = 0)
    total_amount: Mapped[int] = mapped_column(Integer, default = 0)
    
    change_amount: Mapped[int] = mapped_column(Integer, default = 0)
    change_to_deposit: Mapped[bool] = mapped_column(Boolean, default = False)

    __table_args__ = (
        UniqueConstraint("id", "tenant_id", name = "uq_receipt_tenant"),
        CheckConstraint(
            f"""
            (appointment_id IS NOT NULL AND receipt_type = 'appointment')
            OR
            (appointment_id IS NULL AND receipt_type <> 'appointment')
            """,
            name="ck_receipt_appointment_consistency",
        ),
        Index(
            "idx_unique_active_receipt_per_appointment",
            "appointment_id",
            "tenant_id",
            postgresql_where = text("status IN ('pending', 'paid') AND appointment_id IS NOT NULL"),
            unique = True
        ),
        ForeignKeyConstraint(
            ["appointment_id", "tenant_id"],
            ["appointments.id", "appointments.tenant_id"],
            ondelete = "RESTRICT",
            name = "fk_receipt_appoinment"
        ),
        ForeignKeyConstraint(
            ["client_id", "tenant_id"],
            ["clients.id", "clients.tenant_id"],
            ondelete = "RESTRICT",
            name = "fk_receipt_client"
        ),
        ForeignKeyConstraint(
            ["created_by_actor_id", "tenant_id"],
            ["actors.id", "actors.tenant_id"],
            ondelete = "SET NULL",
            name = "fk_receipts_created_by_tenant"
        )
    )

    @property
    def paid_amount(self) -> int:
        return sum(transaction.amount for transaction in self.transactions)
    
    @property
    def remaining_amount(self) -> int:
        return max(0, self.total_amount - self.paid_amount)

    @property
    def discount_amount(self) -> int:
        return self.total_amount - self.subtotal_amount
    
    ALLOWED_FILTERS = {"total_amount", "receipt_type", "status", "archived"}