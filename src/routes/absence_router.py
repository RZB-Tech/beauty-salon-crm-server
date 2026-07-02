from fastapi import APIRouter, Depends, status
from src.core.dependencies.uow import UnitOfWork, get_uow_with_context, make_service_dependency
from src.schemas.base import PaginatedResponseSchema, RequestAllObject
from src.schemas.work_schedule.create import AbsenceCreateSchema
from src.schemas.work_schedule.response import AbsenceResponseSchema
from src.schemas.work_schedule.update import AbsenceUpdateSchema
from src.services.absence_service import EmployeeAbsenceService

router = APIRouter()

get_absence_service = make_service_dependency(EmployeeAbsenceService)

@router.post(
    "", 
    response_model=AbsenceResponseSchema, 
    status_code=status.HTTP_201_CREATED
)
async def create(data: AbsenceCreateSchema,
                 absenceService: EmployeeAbsenceService = Depends(get_absence_service)):
    return await absenceService.create(data)

@router.patch(
    "",
    response_model=AbsenceResponseSchema, 
    status_code=status.HTTP_200_OK,
    summary="Update category"
)
async def update(data: AbsenceUpdateSchema,
                 absenceService: EmployeeAbsenceService = Depends(get_absence_service)):
    return await absenceService.update(data)

@router.get(
    "",
    response_model=PaginatedResponseSchema[AbsenceResponseSchema], 
    status_code=status.HTTP_200_OK,
    summary="Get all categories"
)
async def get_all(params: RequestAllObject = Depends(),
                 absenceService: EmployeeAbsenceService = Depends(get_absence_service)):
    return await absenceService.get_all(params)

@router.get(
    "/{id}",
    response_model=AbsenceResponseSchema, 
    status_code=status.HTTP_200_OK,
    summary="Get "
)
async def get(id: int,
                 absenceService: EmployeeAbsenceService = Depends(get_absence_service)):
    return await absenceService.get(id)

@router.delete(
    "/{id}",
    status_code = status.HTTP_204_NO_CONTENT
)
async def delete(id: int,
                 absenceService: EmployeeAbsenceService = Depends(get_absence_service)):
    return await absenceService.delete(id)