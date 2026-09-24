from decimal import Decimal
from enum import StrEnum
from sqlalchemy import (
    ForeignKey,
    Numeric,
    String,
    DateTime,
    func,
    UniqueConstraint
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from src.database.base import Base

class TenantPaymentStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TenantPayments(Base):
    __tablename__ = "tenant_payments"

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id", ondelete = "set null"), nullable = True)
    tenant_snapshot: Mapped[dict] = mapped_column(JSONB)
    amount: Mapped[Decimal] = mapped_column(Numeric(precision = 30, scale = 2))
    status: Mapped[str] = mapped_column(
        String(255), default = TenantPaymentStatus.PENDING, server_default = TenantPaymentStatus.PENDING
    )
    gateway: Mapped[str | None] = mapped_column(String(255), nullable = True)
    gateway_transaction_id: Mapped[str | None] = mapped_column(String(255), nullable = True)
    gateway_metadata: Mapped[dict] = mapped_column(JSONB, default = dict)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("gateway", "gateway_transaction_id", name = "uq_tenant_payments_gateway_transaction"),
    )