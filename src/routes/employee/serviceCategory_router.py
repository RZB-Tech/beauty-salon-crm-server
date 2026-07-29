from fastapi import APIRouter, Depends, status
from src.core.dependencies.permissions import require_permission
from src.core.dependencies.uow import make_service_dependency
from src.core.permissions import PermissionCode
from src.schemas.base import PaginatedResponseSchema
from src.schemas.service_category.create import ServiceCategoryCreateSchema
from src.schemas.service_category.response import ServiceCategoryResponseSchema
from src.schemas.service_category.update import ServiceCategoryUpdateSchema
from src.services.employee.serviceCategory_service import ServiceCategoryService
from src.schemas.base import PaginatedResponseSchema, RequestAllObject

router = APIRouter()

get_category_service = make_service_dependency(ServiceCategoryService)

@router.post(
    "",
    response_model=ServiceCategoryResponseSchema,
    status_code= 201,
    summary="Создать новую категорию услуг",
    description="Создает категорию, к которой затем можно привязывать услуги.",
    dependencies=[Depends(require_permission([PermissionCode.SERVICE_CATEGORY_CREATE]))]
)
async def create(data: ServiceCategoryCreateSchema,
                 categoryService: ServiceCategoryService = Depends(get_category_service)):
    return await categoryService.create(data)

@router.patch(
    "",
    response_model=ServiceCategoryResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Обновить категорию услуг",
    description="Обновляет название или статус архивации категории по её `id`.",
    dependencies=[Depends(require_permission([PermissionCode.SERVICE_CATEGORY_UPDATE]))]
)
async def update(data: ServiceCategoryUpdateSchema,
                 categoryService: ServiceCategoryService = Depends(get_category_service)):
    return await categoryService.update(data)

@router.post(
    "/get-all",
    response_model=PaginatedResponseSchema[ServiceCategoryResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="Получить все категории услуг",
    description="Возвращает постраничный список категорий услуг организации с поддержкой фильтрации.",
    dependencies=[Depends(require_permission([PermissionCode.SERVICE_CATEGORY_READ]))]
)
async def get_all(params: RequestAllObject,
                  categoryService: ServiceCategoryService = Depends(get_category_service)):
    return await categoryService.get_all(params)

@router.get(
    "/{id}",
    response_model=ServiceCategoryResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Получить категорию услуг по ID",
    description="Возвращает категорию услуг по её `id`.",
    dependencies=[Depends(require_permission([PermissionCode.SERVICE_CATEGORY_READ]))]
)
async def get(id: int, categoryService: ServiceCategoryService = Depends(get_category_service)):
    return await categoryService.get(id)

# @router.delete(
#     "/{id}",
#     status_code = 204
# )
# async def delete(id: int, categoryService: ServiceCategoryService = Depends(get_category_service)):
#     return await categoryService.delete(id)

