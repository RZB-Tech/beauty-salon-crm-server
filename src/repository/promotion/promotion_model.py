from enum import StrEnum
from datetime import datetime
from sqlalchemy import String, DateTime, Numeric, Boolean, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import BaseFields

class PromotionType(StrEnum):
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    BOGO = "bogo"

class Promotion(BaseFields):
    __tablename__ = "promotions"

    name: Mapped[str] = mapped_column(String(255))
    promo_type: Mapped[str] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(Text, nullable = True)
    
    discount_value: Mapped[int | None] = mapped_column(Numeric, nullable = True) 
    
    start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # This single column handles Services, Materials, or anything else
    conditions: Mapped[dict] = mapped_column(JSONB)

    __table_args__ = (
        UniqueConstraint("id", "tenant_id", name = "uq_promotion_tenant"),
        UniqueConstraint("name", "tenant_id", name = "uq_promotion_name_tenant"),
    )

    ALLOWED_FILTERS = {"name", "promo_type", "discount_value", "start_time", "end_time", "is_active", "archived"}