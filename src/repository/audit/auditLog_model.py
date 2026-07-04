from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, ForeignKeyConstraint, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base


class AuditLogs(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(Integer)
    table_name: Mapped[str] = mapped_column(String)       
    record_id: Mapped[int] = mapped_column(Integer)        
    action: Mapped[str] = mapped_column(String)           
    field_name: Mapped[str | None] = mapped_column(String, nullable = True)         
    old_value: Mapped[str | None] = mapped_column(String, nullable=True)          
    new_value: Mapped[str | None] = mapped_column(String, nullable=True)    
    changed_by: Mapped[int] = mapped_column(Integer)
    changed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("idx_audit_logs_tenant_date", "tenant_id", "changed_at"),
        ForeignKeyConstraint(
            ["changed_by", "tenant_id"],
            ["staffs.id", "staffs.tenant_id"],
            ondelete = "CASCADE",
            name = "fk_audit_logs_staff"
        )
    )
