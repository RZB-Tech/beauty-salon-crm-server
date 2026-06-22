from sqlalchemy import func, select
from src.database.base import BaseRepository
from src.repository.audit.auditLog_model import AuditLogs
from src.schemas.auditLogs.request import AuditLogsRequestSchema
from src.schemas.base import RequestAllObject

class AuditLogsRepository(BaseRepository):
    async def get_all(self, params: RequestAllObject, data: AuditLogsRequestSchema) -> tuple[list[AuditLogs], int]:
        count_stmt = (select(func.count())
                      .select_from(AuditLogs)
                      .where(AuditLogs.table_name == data.table_name.value,
                             AuditLogs.record_id == data.record_id))
        total_items = await self.db.scalar(count_stmt) or 0
        offset_value = (params.page - 1) * params.pageSize
        stmt = (
            select(AuditLogs)
            .where(AuditLogs.table_name == data.table_name.value,
                    AuditLogs.record_id == data.record_id)
            .order_by(AuditLogs.changed_at)
            .offset(offset_value)
            .limit(params.pageSize)
        )
        result = await self.db.execute(stmt)
        items = list(result.scalars().all())
        return items, total_items