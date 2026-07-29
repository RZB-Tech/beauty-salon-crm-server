from fastapi import APIRouter, Depends, status
from src.core.dependencies.permissions import require_permission
from src.core.dependencies.uow import UnitOfWork, get_uow_with_context, make_service_dependency
from src.core.permissions import PermissionCode
from src.schemas.auditLogs.request import AuditLogsRequestSchema
from src.schemas.auditLogs.response import AuditLogsResponseSchema
from src.schemas.base import PaginatedResponseSchema, PaginationSchema
from src.services.system.auditLogs_service import AuditLogsService
from src.schemas.base import PaginatedResponseSchema

router = APIRouter()

get_auditLogs_service = make_service_dependency(AuditLogsService)

@router.get(
    "",
    response_model=PaginatedResponseSchema[AuditLogsResponseSchema],
    status_code=status.HTTP_200_OK,
    summary = "Получить журнал аудита",
    description = "Возвращает постраничную историю изменений конкретной записи: какое поле было изменено, старое и новое значение, кто и когда внес изменение. Обязательно указать `table_name` и `record_id`.",
    dependencies=[Depends(require_permission([PermissionCode.AUDIT_LOGS_READ]))]
)
async def get_all(data: AuditLogsRequestSchema = Depends(),
                params: PaginationSchema = Depends(),
                  auditLogsService: AuditLogsService = Depends(get_auditLogs_service)):
    return await auditLogsService.get_all(params, data)