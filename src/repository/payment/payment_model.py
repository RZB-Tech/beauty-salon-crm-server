from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKeyConstraint,
    Index,
    Integer, 
    Enum as SQLEnum,
    Text,
    UniqueConstraint,
    text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import BaseFields

if TYPE_CHECKING: 
    from src.repository.appointment.appointment_model import Appointment, AppointmentServices
    from src.repository.material.material_model import Material

class ReceiptStatus(Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"

class ReceiptType(Enum):
    APPOINTMENT = "appointment"
    DIRECT_SALE = "direct sale"

class ReceiptItem(BaseFields):
    __tablename__ = "receipt_items"
    receipt_id: Mapped[int] = mapped_column(Integer)
    material_id: Mapped[int | None] = mapped_column(Integer, nullable = True)
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

    price: Mapped[int] = mapped_column(Integer)
    quantity: Mapped[int] = mapped_column(Integer, default = 1)
    notes: Mapped[str | None] = mapped_column(Text, nullable = True)

    __table_args__ = (
        UniqueConstraint("id", "tenant_id", name = "uq_receipt_item_tenant"),
        CheckConstraint(
            "(material_id IS NOT NULL AND appointment_service_id IS NULL) OR "
            "(material_id IS NULL AND appointment_service_id IS NOT NULL)",
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
        )
    )

    @property
    def subtotal(self) -> int:
        return self.quantity * self.price

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
    
    receipt_type: Mapped[ReceiptType] = mapped_column(
        SQLEnum(ReceiptType, values_callable = lambda e: [m.value for m in e])
    )

    payments: Mapped[list["Payment"]] = relationship(
        back_populates = "receipt",
        primaryjoin = "and_(Receipt.id == Payment.receipt_id, Receipt.tenant_id == Payment.tenant_id)",
        foreign_keys = "[Payment.receipt_id]")
    
    total_amount: Mapped[int] = mapped_column(Integer)
    status: Mapped[ReceiptStatus] = mapped_column(SQLEnum(
        ReceiptStatus, values_callable = lambda e: [m.value for m in e]),
        default = ReceiptStatus.PENDING)
    
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
    )

    @property
    def paid_amount(self) -> int:
        return sum(payment.amount for payment in self.payments)
    
    @property
    def remaining_amount(self) -> int:
        return max(0, self.total_amount - self.paid_amount)
    
    ALLOWED_FILTERS = {"total_amount", "receipt_type", "status", "archived"}

class PaymentMethodsEnum(Enum):
    CASH = "cash"
    CARD = "card"
    DEPOSIT = "deposit"

class Payment(BaseFields):
    __tablename__ = "payments"

    receipt_id: Mapped[int] = mapped_column(Integer)
    receipt: Mapped[Receipt] = relationship(
        back_populates = "payments",
        primaryjoin = "and_(Payment.receipt_id == Receipt.id, Payment.tenant_id == Receipt.tenant_id)",
        foreign_keys = [receipt_id]
        )

    amount: Mapped[int] = mapped_column(Integer)
    method: Mapped[PaymentMethodsEnum] = mapped_column(SQLEnum(
        PaymentMethodsEnum, values_callable = lambda e: [m.value for m in e]))
    
    cancelled: Mapped[bool] = mapped_column(Boolean, default = False, server_default = "false")

    __table_args__ = (
        UniqueConstraint("id", "tenant_id", name = "uq_payment_tenant"),
        ForeignKeyConstraint(
            ["receipt_id", "tenant_id"],
            ["receipts.id", "receipts.tenant_id"],
            ondelete = "RESTRICT",
            name = "fk_payment_receipt"
        )
    )

    ALLOWED_FILTERS = {"amount", "receipt_id", "method", "archived"}