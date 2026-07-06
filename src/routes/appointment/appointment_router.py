from fastapi import APIRouter, Depends, status
from src.core.dependencies.uow import UnitOfWork, get_uow_with_context, make_service_dependency
from src.schemas.appointment.create import AppointmentCreateSchema
from src.schemas.appointment.response import AppointmentResponseSchema
from src.schemas.appointment.update import AppointmentCancelSchema, AppointmentUpdateSchema
from src.schemas.base import PaginatedResponseSchema, RequestAllObject
from src.schemas.payment.response import ReceiptResponseSchema
from src.services.appointment.appointment_service import AppointmentService

router = APIRouter()

get_appointment_service = make_service_dependency(AppointmentService)

@router.post(
    "", 
    response_model=AppointmentResponseSchema, 
    status_code=status.HTTP_201_CREATED
)
async def create(data: AppointmentCreateSchema,
                 appointmentService: AppointmentService = Depends(get_appointment_service)):
    return await appointmentService.create(data)

@router.patch(
    "",
    response_model = AppointmentResponseSchema, 
    status_code= 200
)
async def update(data: AppointmentUpdateSchema,
                appointmentService: AppointmentService = Depends(get_appointment_service)):
    return await appointmentService.update(data)

@router.post(
    "/get-all",
    response_model=PaginatedResponseSchema[AppointmentResponseSchema], 
    status_code=status.HTTP_200_OK
)
async def get_all(params: RequestAllObject,
                 appointmentService: AppointmentService = Depends(get_appointment_service)):
    return await appointmentService.get_all(params)

@router.get(
    "/{id}",
    response_model=AppointmentResponseSchema, 
    status_code=status.HTTP_200_OK
)
async def get(id: int,
                 appointmentService: AppointmentService = Depends(get_appointment_service)):
    return await appointmentService.get(id)

# @router.post(
#     "/get-many",
#     response_model=list[AppointmentResponseSchema], 
#     status_code=status.HTTP_200_OK
# )
# async def get_many(data: list[int],
#                  appointmentService: AppointmentService = Depends(get_appointment_service)):
#     return await appointmentService.get_many(data)

@router.patch(
    "/{id}/cancel",
    response_model = AppointmentResponseSchema,
    status_code = 200
)
async def cancel(data: AppointmentCancelSchema, 
        appointmentService: AppointmentService = Depends(get_appointment_service)):
    return await appointmentService.cancel(data)

# @router.delete(
#     "/{id}",
#     status_code = 204
# )
# async def delete(id: int,
#                  appointmentService: AppointmentService = Depends(get_appointment_service)):
#     return await appointmentService.delete(id)

@router.get(
    "/{id}/receipts", 
    status_code = 200, 
    response_model = list[ReceiptResponseSchema])
async def get_receipts(id: int,
                       appointmentService: AppointmentService = Depends(get_appointment_service)):
    return await appointmentService.get_receipts(id)