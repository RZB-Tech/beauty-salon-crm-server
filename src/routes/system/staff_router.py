from fastapi import APIRouter, Depends
from src.core.dependencies.permissions import require_admin
from src.core.dependencies.uow import make_service_dependency
from src.schemas.base import PaginatedResponseSchema, RequestAllObject
from src.schemas.staff.create import StaffCreateAPISchema
from src.schemas.staff.request import StaffPermissionsUpdateSchema, StaffRolesAssignSchema
from src.schemas.staff.response import StaffCreateResponseSchema, StaffResponseSchema
from src.services.auth.staff_service import StaffService

router = APIRouter(dependencies = [Depends(require_admin)])
get_staff_service = make_service_dependency(StaffService)

@router.post(
    "/create-user",
    response_model = StaffCreateResponseSchema,
    status_code = 201,
    summary = "Создать учетную запись сотрудника",
    description = "Создает учетную запись для входа в систему (логин/пароль). Можно привязать к уже существующему сотруднику (`employee_id`) или указать имя вручную. Если `password` не передан, генерируется случайный пароль, который возвращается в ответе в открытом виде."
)
async def create_user(data: StaffCreateAPISchema,
                      staffService: StaffService = Depends(get_staff_service)):
    return await staffService.create(data)

@router.post(
    "/get-all",
    response_model = PaginatedResponseSchema[StaffResponseSchema],
    status_code = 200,
    summary = "Получить все учетные записи сотрудников",
    description = "Возвращает постраничный список учетных записей сотрудников текущей организации с поддержкой фильтрации."
)
async def get_all(params: RequestAllObject,
                  staffService: StaffService = Depends(get_staff_service)):
    return await staffService.get_all(params)

@router.patch(
    "/roles",
    response_model = StaffResponseSchema,
    status_code = 200,
    summary = "Назначить роли сотруднику",
    description = "Полностью заменяет список ролей сотрудника на переданный `role_ids`. Пустой список снимает с сотрудника все роли."
)
async def assign_roles(data: StaffRolesAssignSchema,
                 staffService: StaffService = Depends(get_staff_service)):
    return await staffService.assign_roles(data)

@router.patch(
    "/permissions",
    response_model = StaffResponseSchema,
    status_code = 200,
    summary = "Задать прямые разрешения сотрудника",
    description = "Полностью заменяет список индивидуальных разрешений сотрудника (не связанных с ролями) на переданный `permissions`."
)
async def update_permissions(data: StaffPermissionsUpdateSchema,
                 staffService: StaffService = Depends(get_staff_service)):
    return await staffService.update_permissions(data)