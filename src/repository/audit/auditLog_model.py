from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base


class AuditLogs(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    table_name: Mapped[str] = mapped_column(String)       
    record_id: Mapped[int] = mapped_column(Integer)        
    action: Mapped[str] = mapped_column(String)           
    field_name: Mapped[str | None] = mapped_column(String, nullable = True)         
    old_value: Mapped[str | None] = mapped_column(String, nullable=True)          
    new_value: Mapped[str | None] = mapped_column(String, nullable=True)    
    changed_by: Mapped[int] = mapped_column(Integer, ForeignKey("staffs.id"))
    changed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
