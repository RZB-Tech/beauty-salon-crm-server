from enum import StrEnum
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Numeric, Boolean, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import BaseFields

class PromotionType(StrEnum):
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    BOGO = "bogo"

class Promotion(BaseFields):
    __tablename__ = "promotions"

    name: Mapped[str] = mapped_column(String(255))
    promo_type: Mapped[str] = mapped_column(String)
    
    # Using Numeric to support percentages (e.g. 15.5) or fixed amounts
    discount_value: Mapped[float] = mapped_column(Numeric) 
    
    start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # This single column handles Services, Materials, or anything else
    conditions: Mapped[dict] = mapped_column(JSONB)

    __table_args__ = (
        UniqueConstraint("name", "tenant_id", name = "uq_promotion_name_tenant"),
    )