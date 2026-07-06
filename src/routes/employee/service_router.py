from fastapi import APIRouter, Depends, File, UploadFile, status
from src.core.dependencies.uow import make_service_dependency
from src.schemas.base import PaginatedResponseSchema, RequestAllObject
from src.schemas.service import ServiceCreateSchema, ServiceResponseSchema, ServiceUpdateSchema
from src.services.employee.service_service import ServiceService

router = APIRouter()

get_service_service = make_service_dependency(ServiceService)

@router.post(
    "", 
    response_model=ServiceResponseSchema, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new service"
)
async def create(data: ServiceCreateSchema,
                serviceService: ServiceService = Depends(get_service_service)):
    return await serviceService.create(data)

@router.patch(
    "",
    response_model=ServiceResponseSchema, 
    status_code=status.HTTP_200_OK,
    summary="Update category"
)
async def update(data: ServiceUpdateSchema,
                serviceService: ServiceService = Depends(get_service_service)):
    return await serviceService.update(data)

@router.post(
    "/get-all",
    response_model=PaginatedResponseSchema[ServiceResponseSchema], 
    status_code=status.HTTP_200_OK,
    summary="Get all categories"
)
async def get_all(params: RequestAllObject,
                serviceService: ServiceService = Depends(get_service_service)):
    return await serviceService.get_all(params)

@router.get(
    "/{id}",
    response_model=ServiceResponseSchema, 
    status_code=status.HTTP_200_OK,
    summary="Get "
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

@router.post("/import")
async def import_services(file: UploadFile = File(...),
                serviceService: ServiceService = Depends(get_service_service)):
    return await serviceService.import_excel(file = file)