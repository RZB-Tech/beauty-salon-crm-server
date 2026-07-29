from fastapi import APIRouter, Depends, File, UploadFile, status
from src.core.dependencies.permissions import require_permission
from src.core.dependencies.uow import make_service_dependency
from src.core.permissions import PermissionCode
from src.schemas.base import PaginatedResponseSchema, RequestAllObject
from src.schemas.service.create import ServiceCreateSchema
from src.schemas.service.response import ServiceResponseSchema
from src.schemas.service.update import ServiceUpdateSchema
from src.services.employee.service_service import ServiceService

router = APIRouter()

get_service_service = make_service_dependency(ServiceService)

@router.post(
    "",
    response_model=ServiceResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новую услугу",
    description = "`estimated_time` указывается в минутах",
    dependencies=[Depends(require_permission([PermissionCode.SERVICE_CREATE]))]
)
async def create(data: ServiceCreateSchema,
                serviceService: ServiceService = Depends(get_service_service)):
    return await serviceService.create(data)

@router.patch(
    "",
    response_model=ServiceResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Обновить услугу",
    description="Обновляет название, цену, длительность, категорию или статус архивации услуги по её `id`. Нельзя привязать архивированную категорию.",
    dependencies=[Depends(require_permission([PermissionCode.SERVICE_UPDATE]))]
)
async def update(data: ServiceUpdateSchema,
                serviceService: ServiceService = Depends(get_service_service)):
    return await serviceService.update(data)

@router.post(
    "/get-all",
    response_model=PaginatedResponseSchema[ServiceResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="Получить все услуги",
    description="Возвращает постраничный список услуг организации с поддержкой фильтрации.",
    dependencies=[Depends(require_permission([PermissionCode.SERVICE_READ]))]
)
async def get_all(params: RequestAllObject,
                serviceService: ServiceService = Depends(get_service_service)):
    return await serviceService.get_all(params)

@router.get(
    "/{id}",
    response_model=ServiceResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Получить услугу по ID",
    description="Возвращает услугу по её `id`.",
    dependencies=[Depends(require_permission([PermissionCode.SERVICE_READ]))]
)
async def get(id: int,
                serviceService: ServiceService = Depends(get_service_service)):
    return await serviceService.get(id)

# @router.delete(
#     "/{id}",
#     status_code = status.HTTP_204_NO_CONTENT
# )
# async def delete(id: int,
#                 serviceService: ServiceService = Depends(get_service_service)):
#     return await serviceService.delete(id)

@router.post(
    "/import",
    summary="Импортировать услуги из Excel",
    description="Загружает Excel-файл со столбцами `service_category`, `service` и `price`. Для каждой строки создает категорию услуг (если её ещё нет) и саму услугу; строки с уже существующим названием услуги пропускаются.",
    dependencies=[Depends(require_permission([PermissionCode.SERVICE_IMPORT]))]
)
async def import_services(file: UploadFile = File(...),
                serviceService: ServiceService = Depends(get_service_service)):
    return await serviceService.import_excel(file = file)