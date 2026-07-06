from fastapi import APIRouter, Depends, File, UploadFile, status
from src.core.dependencies.uow import make_service_dependency
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
    summary="Create a new specialization"
)
async def create(data: SpecializationCreateSchema,
                specializationService: SpecializationService = Depends(get_specialization_service)):
    return await specializationService.create(data)

@router.patch(
    "",
    response_model=SpecializationResponseSchema, 
    status_code=status.HTTP_200_OK,
    summary="Update specialization"
)
async def update(data: SpecializationUpdateSchema,
                specializationService: SpecializationService = Depends(get_specialization_service)):
    return await specializationService.update(data)

@router.post(
    "/get-all",
    response_model=PaginatedResponseSchema[SpecializationResponseSchema], 
    status_code=status.HTTP_200_OK,
    summary="Get all specializations"
)
async def get_all(params: RequestAllObject,
                specializationService: SpecializationService = Depends(get_specialization_service)):
    return await specializationService.get_all(params)

@router.get(
    "/{id}",
    response_model=SpecializationResponseSchema, 
    status_code=status.HTTP_200_OK,
    summary="Get "
)
async def get(id: int,
                specializationService: SpecializationService = Depends(get_specialization_service)):
    return await specializationService.get(id)

@router.delete("/{id}", status_code = 204)
async def delete(id: int,
                specializationService: SpecializationService = Depends(get_specialization_service)):
    return await specializationService.delete(id)