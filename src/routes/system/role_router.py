from fastapi import APIRouter, Depends, status
from src.core.dependencies.permissions import require_admin
from src.core.dependencies.uow import make_service_dependency
from src.schemas.base import PaginatedResponseSchema, RequestAllObject
from src.schemas.role.create import RoleCreateSchema
from src.schemas.role.response import RoleResponseSchema
from src.schemas.role.update import RoleUpdateSchema
from src.services.auth.role_service import RoleService

router = APIRouter(dependencies = [Depends(require_admin)])
get_role_service = make_service_dependency(RoleService)

@router.post(
    "",
    response_model = RoleResponseSchema,
    status_code = 201,
    summary = "Создать новую роль",
    description = "Создает роль с заданным набором разрешений. Роль можно затем назначить одному или нескольким сотрудникам."
)
async def create(data: RoleCreateSchema,
                 roleService: RoleService = Depends(get_role_service)):
    return await roleService.create(data)

@router.patch(
    "",
    response_model = RoleResponseSchema,
    status_code = status.HTTP_200_OK,
    summary = "Обновить роль",
    description = "Обновляет название, описание, набор разрешений или статус архивации роли по её `id`. Передаются только изменяемые поля."
)
async def update(data: RoleUpdateSchema,
                 roleService: RoleService = Depends(get_role_service)):
    return await roleService.update(data)

@router.post(
    "/get-all",
    response_model = PaginatedResponseSchema[RoleResponseSchema],
    status_code = 200,
    summary = "Получить все роли",
    description = "Возвращает постраничный список ролей организации с поддержкой фильтрации."
)
async def get_all(params: RequestAllObject,
                 roleService: RoleService = Depends(get_role_service)):
    return await roleService.get_all(params)

@router.get(
    "/{id}",
    response_model = RoleResponseSchema,
    status_code = 200,
    summary = "Получить роль по ID",
    description = "Возвращает роль вместе со списком её разрешений."
)
async def get(id: int,
                 roleService: RoleService = Depends(get_role_service)):
    return await roleService.get(id)