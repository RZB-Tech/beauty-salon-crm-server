from typing import Literal

from fastapi import APIRouter, Depends, status

from src.core.dependencies.permissions import require_parent_tenant, require_permission
from src.core.dependencies.uow import make_service_dependency
from src.core.permissions import PermissionCode
from src.schemas.tenant.create import TenantBranchCreateSchema
from src.schemas.tenant.response import TenantBranchCreateResponseSchema, TenantBranchResponseSchema
from src.schemas.tenant.update import UpdateBranchAdminPassword
from src.services.system.tenantBranches_service import TenantBranchesService

router = APIRouter()

get_tenant_branches_service = make_service_dependency(TenantBranchesService)

@router.post(
    "",
    response_model = TenantBranchCreateResponseSchema,
    status_code = status.HTTP_201_CREATED,
    summary = "Создать филиал",
    description = "Создает новый филиал (дочернюю организацию) и его администратора. Доступно только головной организации — у филиала создавать свои филиалы нельзя.",
    dependencies = [
        Depends(require_permission([PermissionCode.TENANT_BRANCH_CREATE])),
        Depends(require_parent_tenant),
    ]
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
    dependencies = [
        Depends(require_permission([PermissionCode.TENANT_BRANCH_READ])),
        Depends(require_parent_tenant),
    ]
)
async def get_all(tenantBranchesService: TenantBranchesService = Depends(get_tenant_branches_service)):
    return await tenantBranchesService.get_all()

@router.post(
    "/reset-admin-password",
    status_code = 200,
    summary = "Сбрасывает / обновляет пароль админа из выбранного филиала",
    description = """Сбрасывает или обновляет пароль админа.
    Указывается `branch_id` (id филиала), `admin_id` (id админа).
    Поле `password` опционален, если не указывается - новый пароль генерируется случайным образом и в ответе возвращает сгенерированный пароль.
    В указанном `password` возвращает пустой ответ
    """,
    dependencies = [
        Depends(require_parent_tenant),
    ]
)
async def get_all(
    data: UpdateBranchAdminPassword,
    tenantBranchesService: TenantBranchesService = Depends(get_tenant_branches_service)):
    return await tenantBranchesService.reset_admin_password(data)