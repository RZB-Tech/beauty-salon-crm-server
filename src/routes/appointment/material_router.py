from fastapi import APIRouter, Depends, status
from src.core.dependencies.permissions import require_permission
from src.core.dependencies.uow import make_service_dependency
from src.core.permissions import PermissionCode
from src.schemas.base import PaginatedResponseSchema, RequestAllObject
from src.schemas.material.create import MaterialCreateSchema
from src.schemas.material.response import MaterialResponseSchema
from src.schemas.material.update import MaterialQuantityUpdateSchema, MaterialUpdateSchema
from src.services.appointment.material_service import MaterialService

router = APIRouter()
get_material_service = make_service_dependency(MaterialService)

@router.post(
    "",
    response_model=MaterialResponseSchema,
    status_code= 201,
    summary="Создать новый материал",
    description="Создает материал (товар для продажи или расходник) с указанным начальным количеством на складе.",
    dependencies=[Depends(require_permission([PermissionCode.MATERIAL_CREATE]))]
)
async def create(data: MaterialCreateSchema,
                 materialService: MaterialService = Depends(get_material_service)):
    return await materialService.create(data)

@router.patch(
    "",
    response_model=MaterialResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Обновить материал",
    description="Обновляет артикул, название, описание, единицу измерения, объем, цену продажи или статус архивации материала по его `id`.",
    dependencies=[Depends(require_permission([PermissionCode.MATERIAL_UPDATE]))]
)
async def update(data: MaterialUpdateSchema,
                 materialService: MaterialService = Depends(get_material_service)):
    return await materialService.update(data)

@router.post(
    "/get-all",
    response_model=PaginatedResponseSchema[MaterialResponseSchema],
    status_code = 200,
    summary="Получить все материалы",
    description="Возвращает постраничный список материалов организации с поддержкой фильтрации.",
    dependencies=[Depends(require_permission([PermissionCode.MATERIAL_READ]))]
)
async def get_all(params: RequestAllObject,
                 materialService: MaterialService = Depends(get_material_service)):
    return await materialService.get_all(params)

@router.get(
    "/{id}",
    response_model=MaterialResponseSchema,
    status_code = 200,
    summary="Получить материал по ID",
    description="Возвращает материал по его `id`.",
    dependencies=[Depends(require_permission([PermissionCode.MATERIAL_READ]))]
)
async def get(id: int,
                 materialService: MaterialService = Depends(get_material_service)):
    return await materialService.get(id)

# @router.delete(
#     "/{id}",
#     status_code = status.HTTP_204_NO_CONTENT
# )
# async def delete(id: int,
#                  materialService: MaterialService = Depends(get_material_service)):
#     return await materialService.delete(id)

@router.post(
    "/update-quantity",
    status_code = status.HTTP_200_OK,
    response_model = MaterialResponseSchema,
    summary = "Обновить количество материала",
    description = "Изменяет количество материала на складе. Для добавления количества: `operation: 1`; для списания: `operation: -1`.",
    name = "Обновить количество",
    dependencies=[Depends(require_permission([PermissionCode.MATERIAL_UPDATE_QUANTITY]))]
)
async def update_deposit(data: MaterialQuantityUpdateSchema,
                 materialService: MaterialService = Depends(get_material_service)):
    return await materialService.updateQuantity(data)