from typing import Any, Optional
from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, INTEGER
from sqlalchemy.orm import Mapped, mapped_column
from src.database.base import BaseFields

class Segmentation(BaseFields):
    __tablename__ = "segmentations"

    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    criteria: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    client_ids: Mapped[list[int]] = mapped_column(ARRAY(INTEGER), nullable=False, default=list)