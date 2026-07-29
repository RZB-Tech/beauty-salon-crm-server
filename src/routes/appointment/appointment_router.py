from fastapi import APIRouter, Depends, status
from src.core.dependencies.permissions import require_permission
from src.core.dependencies.uow import UnitOfWork, get_uow_with_context, make_service_dependency
from src.core.permissions import PermissionCode
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
    status_code = 201,
    summary = "Создать посещение",
    description = "Создает посещение клиента с необязательным сразу заполненным списком записей (`records`): по сотруднику и оказанным им услугам/товарам.",
    dependencies=[Depends(require_permission([PermissionCode.APPOINTMENT_CREATE]))]
)
async def create(data: AppointmentCreateSchema,
                 appointmentService: AppointmentService = Depends(get_appointment_service)):
    return await appointmentService.create(data)

@router.patch(
    "",
    response_model = AppointmentResponseSchema,
    status_code= 200,
    summary = "Обновить посещение",
    description = "Обновляет статус (`awaiting` / `started` / `finished`), заметки или статус архивации посещения по его `id`.",
    dependencies=[Depends(require_permission([PermissionCode.APPOINTMENT_UPDATE]))]
)
async def update(data: AppointmentUpdateSchema,
                appointmentService: AppointmentService = Depends(get_appointment_service)):
    return await appointmentService.update(data)

@router.post(
    "/get-all",
    response_model=PaginatedResponseSchema[AppointmentResponseSchema],
    status_code=status.HTTP_200_OK,
    summary = "Получить все посещения",
    description = "Возвращает постраничный список посещений организации с поддержкой фильтрации.",
    dependencies=[Depends(require_permission([PermissionCode.APPOINTMENT_READ]))]
)
async def get_all(params: RequestAllObject,
                 appointmentService: AppointmentService = Depends(get_appointment_service)):
    return await appointmentService.get_all(params)

@router.get(
    "/{id}",
    response_model=AppointmentResponseSchema,
    status_code=status.HTTP_200_OK,
    summary = "Получить посещение по ID",
    dependencies=[Depends(require_permission([PermissionCode.APPOINTMENT_READ]))]
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
    "/cancel",
    response_model = AppointmentResponseSchema,
    status_code = 200,
    summary = "Отменить посещение",
    description = "Отменяет посещение с указанием причины (`reason`). Нельзя отменить уже оплаченное посещение или посещение с активным чеком — их нужно отменить отдельно. Идентификатор посещения передается в теле запроса (`id`), значение `{id}` в пути не используется.",
    dependencies=[Depends(require_permission([PermissionCode.APPOINTMENT_CANCEL]))]
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
    response_model = list[ReceiptResponseSchema],
    summary = "Чеки посещения",
    description = "Возвращает список чеков, связанных с данным посещением.",
    dependencies=[Depends(require_permission([PermissionCode.APPOINTMENT_READ]))])
async def get_receipts(id: int,
                       appointmentService: AppointmentService = Depends(get_appointment_service)):
    return await appointmentService.get_receipts(id)