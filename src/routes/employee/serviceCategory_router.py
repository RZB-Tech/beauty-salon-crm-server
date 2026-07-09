from fastapi import APIRouter, Depends, status
from src.core.dependencies.uow import make_service_dependency
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
    summary="Create a new service category"
)
async def create(data: ServiceCategoryCreateSchema,
                 categoryService: ServiceCategoryService = Depends(get_category_service)):
    return await categoryService.create(data)

@router.patch(
    "",
    response_model=ServiceCategoryResponseSchema, 
    status_code=status.HTTP_200_OK,
    summary="Update category"
)
async def update(data: ServiceCategoryUpdateSchema,
                 categoryService: ServiceCategoryService = Depends(get_category_service)):
    return await categoryService.update(data)

@router.post(
    "/get-all",
    response_model=PaginatedResponseSchema[ServiceCategoryResponseSchema], 
    status_code=status.HTTP_200_OK,
    summary="Get all categories"
)
async def get_all(params: RequestAllObject,
                  categoryService: ServiceCategoryService = Depends(get_category_service)):
    return await categoryService.get_all(params)

@router.get(
    "/{id}",
    response_model=ServiceCategoryResponseSchema, 
    status_code=status.HTTP_200_OK,
    summary="Get category"
)
async def get(id: int, categoryService: ServiceCategoryService = Depends(get_category_service)):
    return await categoryService.get(id)

# @router.delete(
#     "/{id}",
#     status_code = 204
# )
# async def delete(id: int, categoryService: ServiceCategoryService = Depends(get_category_service)):
#     return await categoryService.delete(id)

