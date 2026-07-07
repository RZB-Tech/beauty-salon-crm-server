from sqlalchemy import func, select
from src.database.base import Actor, BaseRepository
from src.repository.audit.auditLog_model import AuditLogs
from src.repository.staff.staff_model import Staff
from src.schemas.auditLogs.request import AuditLogsRequestSchema
from src.schemas.base import RequestAllObject

# class AuditLogsRepository(BaseRepository):
#     async def get_all(self, params: RequestAllObject, data: AuditLogsRequestSchema) -> tuple[list[AuditLogs], int]:
#         count_stmt = (select(func.count())
#                       .select_from(AuditLogs)
#                       .where(AuditLogs.table_name == data.table_name.value,
#                              AuditLogs.record_id == data.record_id))
#         total_items = await self.db.scalar(count_stmt) or 0
#         offset_value = (params.page - 1) * params.pageSize
#         stmt = (
#             select(AuditLogs)
#             .where(AuditLogs.table_name == data.table_name.value,
#                     AuditLogs.record_id == data.record_id)
#             .order_by(AuditLogs.changed_at)
#             .offset(offset_value)
#             .limit(params.pageSize)
#         )
#         result = await self.db.execute(stmt)
#         items = result.scalars().all()
#         return items, total_items

class AuditLogsRepository(BaseRepository):
    async def get_all(
        self, params: RequestAllObject, data: AuditLogsRequestSchema
    ) -> tuple[list[dict], int]: # Changed return type to list[dict] to include extra fields
        
        # 1. Count statement stays simple
        count_stmt = (
            select(func.count())
            .select_from(AuditLogs)
            .where(
                AuditLogs.table_name == data.table_name.value,
                AuditLogs.record_id == data.record_id
            )
        )
        total_items = await self.db.scalar(count_stmt) or 0
        
        # 2. Pagination calculation
        offset_value = (params.page - 1) * params.pageSize
        
        # 3. Comprehensive select statement with Joins
        stmt = (
            select(
                AuditLogs,
                Actor.actor_type,
                # Dynamically build display name; fall back to 'Telegram Bot' or system labels if Staff is missing
                func.coalesce(
                    Staff.firstname + " " + func.coalesce(Staff.lastname, ""),
                    "Telegram Bot" 
                ).label("actor_display_name")
            )
            .join(Actor, AuditLogs.changed_by == Actor.id)
            .outerjoin(Staff, Actor.id == Staff.actor_id)
            .where(
                AuditLogs.table_name == data.table_name.value,
                AuditLogs.record_id == data.record_id
            )
            # PRO-TIP: Audit trails are usually best viewed newest first (.desc())
            .order_by(AuditLogs.changed_at.desc()) 
            .offset(offset_value)
            .limit(params.pageSize)
        )
        
        result = await self.db.execute(stmt)
        
        # 4. Map the multi-column rows into flat dictionaries for easy Pydantic parsing
        items = []
        for row in result.all():
            audit_log = row.AuditLogs
            log_dict = {
                # Pulls all core audit log table fields
                **{c.key: getattr(audit_log, c.key) for c in audit_log.__table__.columns},
                # Injects the polymorphic data
                "actor_type": row.actor_type,
                "actor_display_name": row.actor_display_name
            }
            items.append(log_dict)
            
        return items, total_items # Fixed the typo from 'total_item'