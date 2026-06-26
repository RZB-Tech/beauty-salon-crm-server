from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer, 
    Enum as SQLEnum,
    Text,
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
    receipt_id: Mapped[int] = mapped_column(ForeignKey("receipts.id"))
    material_id: Mapped[int] = mapped_column(ForeignKey("materials.id"), nullable = True)
    appointment_service_id: Mapped[int] = mapped_column(ForeignKey("appointment_services.id"), nullable = True)

    price: Mapped[int] = mapped_column(Integer)
    quantity: Mapped[int] = mapped_column(Integer, default = 1)

    receipt: Mapped["Receipt"] = relationship(back_populates = "items")
    material: Mapped["Material"] = relationship()
    appointment_service: Mapped["AppointmentServices"] = relationship()

    notes: Mapped[str | None] = mapped_column(Text, nullable = True)

    __table_args__ = (
        CheckConstraint(
            "(material_id IS NOT NULL AND appointment_service_id IS NULL) OR "
            "(material_id IS NULL AND appointment_service_id IS NOT NULL)",
            name="chk_receipt_item_exclusive_source"
        ),
    )

    @property
    def subtotal(self) -> int:
        return self.quantity * self.price

class Receipt(BaseFields):
    __tablename__ = "receipts"

    receipt_type: Mapped[ReceiptType] = mapped_column(
        SQLEnum(ReceiptType, values_callable = lambda e: [m.value for m in e])
    )

    appointment_id: Mapped[int | None] = mapped_column(ForeignKey("appointments.id"), nullable = True)
    appointment: Mapped["Appointment"] = relationship(back_populates = "receipt")
    
    client_id: Mapped[int | None] = mapped_column(ForeignKey("clients.id"), nullable = True)

    items: Mapped[list[ReceiptItem]] = relationship(back_populates = "receipt", cascade = "all, delete-orphan")

    total_amount: Mapped[int] = mapped_column(Integer)
    status: Mapped[ReceiptStatus] = mapped_column(SQLEnum(
        ReceiptStatus, values_callable = lambda e: [m.value for m in e]),
        default = ReceiptStatus.PENDING)
    
    change_amount: Mapped[int] = mapped_column(Integer, default = 0)
    change_to_deposit: Mapped[bool] = mapped_column(Boolean, default = False)

    payments: Mapped[list["Payment"]] = relationship(back_populates = "receipt")

    __table_args__ = (
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
            postgresql_where = text("status IN ('pending', 'paid') AND appointment_id IS NOT NULL"),
            unique = True
        )
    )

    @property
    def paid_amount(self) -> int:
        return sum(payment.amount for payment in self.payments)
    
    @property
    def remaining_amount(self) -> int:
        return max(0, self.total_amount - self.paid_amount)
    
    ALLOWED_FILTERS = {"receipt_type", "status"}

class PaymentMethodsEnum(Enum):
    CASH = "cash"
    CARD = "card"
    DEPOSIT = "deposit"

class Payment(BaseFields):
    __tablename__ = "payments"

    receipt_id: Mapped[int] = mapped_column(ForeignKey("receipts.id", ondelete = "CASCADE"))
    receipt: Mapped[Receipt] = relationship(back_populates = "payments")

    amount: Mapped[int] = mapped_column(Integer)
    method: Mapped[PaymentMethodsEnum] = mapped_column(SQLEnum(
        PaymentMethodsEnum, values_callable = lambda e: [m.value for m in e]))

    ALLOWED_FILTERS = {"receipt_id", "method"}