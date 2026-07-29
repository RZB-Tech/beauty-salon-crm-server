from fastapi import APIRouter, Depends, status
from src.core.dependencies.permissions import require_permission
from src.core.dependencies.uow import  make_service_dependency
from src.core.permissions import PermissionCode
from src.schemas.appointment.create import AppointmentServicesCreateSchema
from src.schemas.appointment.response import AppointmentResponseSchema, AppointmentServicesResponseSchema
from src.schemas.appointment.update import AppointmentServiceUpdateSchema
from src.schemas.base import PaginatedResponseSchema, RequestAllObject
from src.services.appointment.appointmentServices_service import AppointmentServicesService

router = APIRouter()

get_appointment_services_service = make_service_dependency(AppointmentServicesService)

@router.post(
    "",
    response_model=AppointmentResponseSchema,
    status_code = 201,
    summary = "Добавить услугу/товар в запись посещения",
    description = "Добавляет к записи посещения (`appointment_record_id`) либо услугу (`service_id`), либо товар (`material_id`) — указывается ровно одно из двух. Если фактическая цена отличается от базовой, необходимо указать причину (`price_changed_reason`).",
    dependencies=[Depends(require_permission([PermissionCode.APPOINTMENT_SERVICES_CREATE]))]
)
async def create(data: AppointmentServicesCreateSchema,
                 appointmentServicesService: AppointmentServicesService = Depends(get_appointment_services_service)):
    return await appointmentServicesService.create(data)

@router.patch(
    "",
    response_model=AppointmentResponseSchema,
    status_code = 200,
    summary = "Обновить услугу/товар в записи посещения",
    description = "Обновляет количество, цену или причину изменения цены оказанной услуги/использованного товара по `id`.",
    dependencies=[Depends(require_permission([PermissionCode.APPOINTMENT_SERVICES_UPDATE]))]
)
async def update(data: AppointmentServiceUpdateSchema,
    appointmentServicesService: AppointmentServicesService = Depends(get_appointment_services_service)):
    return await appointmentServicesService.update(data)

# @router.get(
#     "",
#     response_model=PaginatedResponseSchema[AppointmentServicesResponseSchema], 
#     status_code=status.HTTP_200_OK
# )
# async def get_all(params: RequestAllObject = Depends(),
#                  appointmentServicesService: AppointmentServicesService = Depends(get_appointment_services_service)):
#     return await appointmentServicesService.get_all(params)

# @router.get(
#     "/{id}",
#     response_model=AppointmentServicesResponseSchema, 
#     status_code=status.HTTP_200_OK
# )
# async def get(id: int,
#                  appointmentServicesService: AppointmentServicesService = Depends(get_appointment_services_service)):
#     return await appointmentServicesService.get(id)

# @router.post(
#     "/get-many",
#     response_model=list[AppointmentServicesResponseSchema], 
#     status_code=status.HTTP_200_OK
# )
# async def get_many(data: list[int],
#                  appointmentServicesService: AppointmentServicesService = Depends(get_appointment_services_service)):
#     return await appointmentServicesService.get_many(data)

@router.delete(
    "/{id}",
    status_code = 200,
    response_model = AppointmentResponseSchema,
    summary = "Удалить услугу/товар из записи посещения",
    description = "Безвозвратно удаляет оказанную услугу/использованный товар из записи посещения по её `id`.",
    dependencies=[Depends(require_permission([PermissionCode.APPOINTMENT_SERVICES_DELETE]))]
)
async def delete(id: int,
                 appointmentServicesService: AppointmentServicesService = Depends(get_appointment_services_service)):
    return await appointmentServicesService.delete(id)