from fastapi import APIRouter, Depends, status

from src.core.dependencies.permissions import require_permission
from src.core.dependencies.uow import make_service_dependency
from src.core.permissions import PermissionCode
from src.schemas.tenant.create import TenantBranchCreateSchema
from src.schemas.tenant.response import TenantBranchCreateResponseSchema, TenantBranchResponseSchema
from src.services.system.tenantBranches_service import TenantBranchesService

router = APIRouter()

get_tenant_branches_service = make_service_dependency(TenantBranchesService)

@router.post(
    "",
    response_model = TenantBranchCreateResponseSchema,
    status_code = status.HTTP_201_CREATED,
    summary = "Создать филиал",
    description = "Создает новый филиал (дочернюю организацию) и его администратора. Доступно только головной организации — у филиала создавать свои филиалы нельзя.",
    dependencies = [Depends(require_permission([PermissionCode.TENANT_BRANCH_CREATE]))]
)
async def create(data: TenantBranchCreateSchema,
                 tenantBranchesService: TenantBranchesService = Depends(get_tenant_branches_service)):
    return await tenantBranchesService.create(data)

@router.get(
    "",
    response_model = list[TenantBranchResponseSchema],
    status_code = status.HTTP_200_OK,
    summary = "Список филиалов",
    description = "Возвращает список филиалов текущей организации.",
    dependencies = [Depends(require_permission([PermissionCode.TENANT_BRANCH_READ]))]
)
async def get_all(tenantBranchesService: TenantBranchesService = Depends(get_tenant_branches_service)):
    return await tenantBranchesService.get_all()
