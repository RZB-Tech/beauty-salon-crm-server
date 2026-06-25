from fastapi import APIRouter, Depends, status
from src.core.dependencies.uow import make_service_dependency
from src.schemas.base import PaginatedResponseSchema, RequestAllObject
from src.schemas.material.create import MaterialCreateSchema
from src.schemas.material.response import MaterialResponseSchema
from src.schemas.material.update import MaterialQuantityUpdateSchema, MaterialUpdateSchema
from src.services.material_service import MaterialService

router = APIRouter()
get_material_service = make_service_dependency(MaterialService)

@router.post(
    "/", 
    response_model=MaterialResponseSchema, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new service"
)
async def create(data: MaterialCreateSchema,
                 materialService: MaterialService = Depends(get_material_service)):
    return await materialService.create(data)

@router.patch(
    "/",
    response_model=MaterialResponseSchema, 
    status_code=status.HTTP_200_OK,
    summary="Update category"
)
async def update(data: MaterialUpdateSchema,
                 materialService: MaterialService = Depends(get_material_service)):
    return await materialService.update(data)

@router.post(
    "/get-all",
    response_model=PaginatedResponseSchema[MaterialResponseSchema], 
    status_code=status.HTTP_200_OK,
    summary="Get all categories"
)
async def get_all(params: RequestAllObject,
                 materialService: MaterialService = Depends(get_material_service)):
    return await materialService.get_all(params)

@router.get(
    "/{id}",
    response_model=MaterialResponseSchema, 
    status_code=status.HTTP_200_OK,
    summary="Get "
)
async def get(id: int,
                 materialService: MaterialService = Depends(get_material_service)):
    return await materialService.get(id)

@router.delete(
    "/{id}",
    status_code = status.HTTP_204_NO_CONTENT
)
async def delete(id: int,
                 materialService: MaterialService = Depends(get_material_service)):
    return await materialService.delete(id)

@router.post(
    "/update-quantity",
    status_code = status.HTTP_200_OK,
    response_model = MaterialResponseSchema,
    description = "Для добавления количества: operaion: 1\nДля отнятия количества: operataion: -1",
    name = "Обновить количество"
)
async def update_deposit(data: MaterialQuantityUpdateSchema,
                 materialService: MaterialService = Depends(get_material_service)):
    return await materialService.updateQuantity(data)