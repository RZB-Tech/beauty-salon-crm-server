from fastapi import APIRouter, Depends, File, UploadFile, status
from src.core.dependencies.permissions import require_permission
from src.core.dependencies.uow import make_service_dependency
from src.core.permissions import PermissionCode
from src.schemas.base import PaginatedResponseSchema, RequestAllObject
from src.schemas.specialization.create import SpecializationCreateSchema
from src.schemas.specialization.response import SpecializationResponseSchema
from src.schemas.specialization.update import SpecializationUpdateSchema
from src.services.employee.specialization_service import SpecializationService

router = APIRouter()

get_specialization_service = make_service_dependency(SpecializationService)

@router.post(
    "",
    response_model=SpecializationResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новую специализацию",
    description="Создает специализацию сотрудников (например, «Парикмахер-стилист»), которую затем можно присвоить сотруднику.",
    dependencies=[Depends(require_permission([PermissionCode.SPECIALIZATION_CREATE]))]
)
async def create(data: SpecializationCreateSchema,
                specializationService: SpecializationService = Depends(get_specialization_service)):
    return await specializationService.create(data)

@router.patch(
    "",
    response_model=SpecializationResponseSchema,
    status_code= 200,
    summary="Обновить специализацию",
    description="Обновляет название или статус архивации специализации по её `id`.",
    dependencies=[Depends(require_permission([PermissionCode.SPECIALIZATION_UPDATE]))]
)
async def update(data: SpecializationUpdateSchema,
                specializationService: SpecializationService = Depends(get_specialization_service)):
    return await specializationService.update(data)

@router.post(
    "/get-all",
    response_model=PaginatedResponseSchema[SpecializationResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="Получить все специализации",
    description="Возвращает постраничный список специализаций организации с поддержкой фильтрации.",
    dependencies=[Depends(require_permission([PermissionCode.SPECIALIZATION_READ]))]
)
async def get_all(params: RequestAllObject,
                specializationService: SpecializationService = Depends(get_specialization_service)):
    return await specializationService.get_all(params)

@router.get(
    "/{id}",
    response_model=SpecializationResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Получить специализацию по ID",
    description="Возвращает специализацию по её `id`.",
    dependencies=[Depends(require_permission([PermissionCode.SPECIALIZATION_READ]))]
)
async def get(id: int,
                specializationService: SpecializationService = Depends(get_specialization_service)):
    return await specializationService.get(id)

# @router.delete(
#     "/{id}",
#     status_code = 204,
#     dependencies=[Depends(require_permission([PermissionCode.SPECIALIZATION_DELETE]))]
# )
# async def delete(id: int,
#                 specializationService: SpecializationService = Depends(get_specialization_service)):
#     return await specializationService.delete(id)