import math
from src.core.dependencies.uow import UnitOfWork
from src.schemas.auditLogs.request import AuditLogsRequestSchema
from src.schemas.base import PaginationSchema, RequestAllObject

class AuditLogsService():
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
    
    async def get_all(self, params: PaginationSchema, data: AuditLogsRequestSchema ) -> dict:
        items, total_items = await self.uow.auditLogs.get_all(params, data)

        total_pages = math.ceil(total_items / params.pageSize) if params.pageSize > 0 else 0
        
        return {
            "items": items,
            "page": params.page,
            "pageSize": params.pageSize,
            "totalItems": total_items,
            "totalPages": total_pages
        }
    
    