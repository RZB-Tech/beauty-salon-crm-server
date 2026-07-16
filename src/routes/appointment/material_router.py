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
    summary="Create a new material",
    dependencies=[Depends(require_permission([PermissionCode.MATERIAL_CREATE]))]
)
async def create(data: MaterialCreateSchema,
                 materialService: MaterialService = Depends(get_material_service)):
    return await materialService.create(data)

@router.patch(
    "",
    response_model=MaterialResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Update category",
    dependencies=[Depends(require_permission([PermissionCode.MATERIAL_UPDATE]))]
)
async def update(data: MaterialUpdateSchema,
                 materialService: MaterialService = Depends(get_material_service)):
    return await materialService.update(data)

@router.post(
    "/get-all",
    response_model=PaginatedResponseSchema[MaterialResponseSchema],
    status_code = 200,
    summary="Get all categories",
    dependencies=[Depends(require_permission([PermissionCode.MATERIAL_READ]))]
)
async def get_all(params: RequestAllObject,
                 materialService: MaterialService = Depends(get_material_service)):
    return await materialService.get_all(params)

@router.get(
    "/{id}",
    response_model=MaterialResponseSchema,
    status_code = 200,
    summary="Get ",
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
    description = "Для добавления количества: operaion: 1\nДля отнятия количества: operataion: -1",
    name = "Обновить количество",
    dependencies=[Depends(require_permission([PermissionCode.MATERIAL_UPDATE_QUANTITY]))]
)
async def update_deposit(data: MaterialQuantityUpdateSchema,
                 materialService: MaterialService = Depends(get_material_service)):
    return await materialService.updateQuantity(data)