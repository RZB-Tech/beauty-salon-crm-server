from fastapi import APIRouter, Depends, status
from src.core.dependencies.uow import UnitOfWork, get_uow_with_context
from src.schemas.appointment.create import AppointmentRecordsCreateSchema
from src.schemas.appointment.response import AppointmentRecordsResponseSchema
from src.schemas.base import PaginatedResponseSchema, RequestAllObject
from src.services.appointmentRecords_service import AppointmentRecordsService

router = APIRouter()

def get_appointment_records_service(uow: UnitOfWork = Depends(get_uow_with_context)) -> AppointmentRecordsService:
    return AppointmentRecordsService(uow=uow)

@router.post(
    "/", 
    response_model=AppointmentRecordsResponseSchema, 
    status_code=status.HTTP_201_CREATED
)
async def create(data: AppointmentRecordsCreateSchema,
                 appointmentRecordsService: AppointmentRecordsService = Depends(get_appointment_records_service)):
    return await appointmentRecordsService.create(data)

# @router.patch(
#     "/",
#     response_model=ClientResponseSchema, 
#     status_code=status.HTTP_200_OK
# )
# async def update(data: ClientUpdateSchema):
#     return await ClientService.update(data)

@router.get(
    "/",
    response_model=PaginatedResponseSchema[AppointmentRecordsResponseSchema], 
    status_code=status.HTTP_200_OK
)
async def get_all(params: RequestAllObject = Depends(),
                 appointmentRecordsService: AppointmentRecordsService = Depends(get_appointment_records_service)):
    return await appointmentRecordsService.get_all(params)

@router.get(
    "/{id}",
    response_model=AppointmentRecordsResponseSchema, 
    status_code=status.HTTP_200_OK
)
async def get(id: int,
                 appointmentRecordsService: AppointmentRecordsService = Depends(get_appointment_records_service)):
    return await appointmentRecordsService.get(id)

@router.post(
    "/get-many",
    response_model=list[AppointmentRecordsResponseSchema], 
    status_code=status.HTTP_200_OK
)
async def get_many(data: list[int],
                 appointmentRecordsService: AppointmentRecordsService = Depends(get_appointment_records_service)):
    return await appointmentRecordsService.get_many(data)

@router.delete(
    "/{id}",
    status_code = status.HTTP_204_NO_CONTENT
)
async def delete(id: int,
                 appointmentRecordsService: AppointmentRecordsService = Depends(get_appointment_records_service)):
    return await appointmentRecordsService.delete(id)