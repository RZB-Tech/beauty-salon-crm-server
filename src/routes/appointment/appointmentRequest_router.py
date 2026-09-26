from fastapi import APIRouter, Depends, status
from src.core.dependencies.permissions import require_permission
from src.core.dependencies.uow import make_service_dependency
from src.core.permissions import PermissionCode
from src.schemas.appointmentRequest.response import AppointmentRequestResponseSchema
from src.schemas.appointmentRequest.update import AppointmentRequestConfirmSchema, AppointmentRequestDeclineSchema
from src.schemas.base import PaginatedResponseSchema, RequestAllObject
from src.schemas.client.response import ClientResponseSchema
from src.services.appointment.appointmentRequest_service import AppointmentRequestService

router = APIRouter()

get_appointment_request_service = make_service_dependency(AppointmentRequestService)

@router.post(
    "/get-all",
    response_model = PaginatedResponseSchema[AppointmentRequestResponseSchema],
    status_code = status.HTTP_200_OK,
    summary = "Получить все заявки на запись",
    description = "Постраничный список заявок на запись из Telegram с поддержкой фильтрации (например, `{\"status\": \"pending\"}` — ожидающие решения).",
    dependencies = [Depends(require_permission([PermissionCode.APPOINTMENT_REQUESTS_READ]))]
)
async def get_all(params: RequestAllObject,
                  appointmentRequestService: AppointmentRequestService = Depends(get_appointment_request_service)):
    return await appointmentRequestService.get_all(params)

@router.patch(
    "/confirm",
    response_model = AppointmentRequestResponseSchema,
    status_code = status.HTTP_200_OK,
    summary = "Подтвердить заявку на запись",
    description = "Создает посещение (`created_via = telegram`) так, как решил сотрудник: время (`start_time_est`, `end_time_est`), сотрудники и услуги (`records`) — предзаполните из `services` и `start_time_est` заявки. Заявка переходит в `confirmed`, клиенту приходит сообщение от бота. Клиент организации: `client_id`, если передан (привязывается к Telegram-клиенту); иначе ранее привязанный клиент; иначе создается новый из профиля Telegram с номером `new_client_phone` (сотрудник выбирает `telegram_phone` или `call_phone`; по умолчанию `call_phone`, затем `telegram_phone`) — с учетом лимита клиентов тарифа. Действуют все проверки создания посещения (график, занятость сотрудника и т.д.).",
    dependencies = [Depends(require_permission([PermissionCode.APPOINTMENT_REQUESTS_CONFIRM]))]
)
async def confirm(data: AppointmentRequestConfirmSchema,
                  appointmentRequestService: AppointmentRequestService = Depends(get_appointment_request_service)):
    return await appointmentRequestService.confirm(data)

@router.patch(
    "/decline",
    response_model = AppointmentRequestResponseSchema,
    status_code = status.HTTP_200_OK,
    summary = "Отклонить заявку на запись",
    description = "Переводит ожидающую заявку в `declined` с обязательной причиной (`reason`) — клиенту приходит сообщение от бота с этой причиной.",
    dependencies = [Depends(require_permission([PermissionCode.APPOINTMENT_REQUESTS_DECLINE]))]
)
async def decline(data: AppointmentRequestDeclineSchema,
                  appointmentRequestService: AppointmentRequestService = Depends(get_appointment_request_service)):
    return await appointmentRequestService.decline(data)

@router.get(
    "/{id}",
    response_model = AppointmentRequestResponseSchema,
    status_code = status.HTTP_200_OK,
    summary = "Получить заявку на запись по ID",
    dependencies = [Depends(require_permission([PermissionCode.APPOINTMENT_REQUESTS_READ]))]
)
async def get(id: int,
              appointmentRequestService: AppointmentRequestService = Depends(get_appointment_request_service)):
    return await appointmentRequestService.get(id)

@router.get(
    "/{id}/matching-clients",
    response_model = list[ClientResponseSchema],
    status_code = status.HTTP_200_OK,
    summary = "Подходящие клиенты для заявки",
    description = "Клиенты организации, уже привязанные к Telegram-клиенту заявки (по `global_client_id` или `telegram_user_id`) или совпадающие с ним по номеру телефона (`telegram_phone`, `call_phone`) — чтобы выбрать `client_id` при подтверждении и не создавать дубликат.",
    dependencies = [Depends(require_permission([PermissionCode.APPOINTMENT_REQUESTS_READ, PermissionCode.CLIENT_READ]))]
)
async def get_matching_clients(id: int,
                               appointmentRequestService: AppointmentRequestService = Depends(get_appointment_request_service)):
    return await appointmentRequestService.get_matching_clients(id)
