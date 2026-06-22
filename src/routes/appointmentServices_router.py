from fastapi import APIRouter, Depends, status
from src.core.dependencies.uow import UnitOfWork, get_uow_with_context
from src.schemas.appointment.create import AppointmentServicesCreateSchema
from src.schemas.appointment.response import AppointmentServicesResponseSchema
from src.schemas.base import PaginatedResponseSchema, RequestAllObject
from src.services.appointmentServices_service import AppointmentServicesService

router = APIRouter()

def get_appointment_services_service(uow: UnitOfWork = Depends(get_uow_with_context)) -> AppointmentServicesService:
    return AppointmentServicesService(uow=uow)

@router.post(
    "/", 
    response_model=AppointmentServicesResponseSchema, 
    status_code=status.HTTP_201_CREATED
)
async def create(data: AppointmentServicesCreateSchema,
                 appointmentServicesService: AppointmentServicesService = Depends(get_appointment_services_service)):
    return await appointmentServicesService.create(data)

# @router.patch(
#     "/",
#     response_model=ClientResponseSchema, 
#     status_code=status.HTTP_200_OK
# )
# async def update(data: ClientUpdateSchema):
#     return await ClientService.update(data)

@router.get(
    "/",
    response_model=PaginatedResponseSchema[AppointmentServicesResponseSchema], 
    status_code=status.HTTP_200_OK
)
async def get_all(params: RequestAllObject = Depends(),
                 appointmentServicesService: AppointmentServicesService = Depends(get_appointment_services_service)):
    return await appointmentServicesService.get_all(params)

@router.get(
    "/{id}",
    response_model=AppointmentServicesResponseSchema, 
    status_code=status.HTTP_200_OK
)
async def get(id: int,
                 appointmentServicesService: AppointmentServicesService = Depends(get_appointment_services_service)):
    return await appointmentServicesService.get(id)

@router.post(
    "/get-many",
    response_model=list[AppointmentServicesResponseSchema], 
    status_code=status.HTTP_200_OK
)
async def get_many(data: list[int],
                 appointmentServicesService: AppointmentServicesService = Depends(get_appointment_services_service)):
    return await appointmentServicesService.get_many(data)

@router.delete(
    "/{id}",
    status_code = status.HTTP_204_NO_CONTENT
)
async def delete(id: int,
                 appointmentServicesService: AppointmentServicesService = Depends(get_appointment_services_service)):
    return await appointmentServicesService.delete(id)