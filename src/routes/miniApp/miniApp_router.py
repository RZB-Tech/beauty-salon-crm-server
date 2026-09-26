from fastapi import APIRouter, Depends, status
from src.core.dependencies.miniApp import get_current_global_client, get_telegram_user
from src.core.dependencies.uow import make_service_dependency
from src.repository.globalClient.globalClient_model import GlobalClient
from src.schemas.appointmentRequest.create import AppointmentRequestCreateSchema
from src.schemas.appointmentRequest.response import (
    MiniAppAppointmentRequestResponseSchema, MiniAppServiceResponseSchema, MiniAppTenantResponseSchema)
from src.schemas.appointmentRequest.update import AppointmentRequestClientCancelSchema
from src.schemas.base import PaginatedResponseSchema, PaginationSchema
from src.schemas.globalClient.create import GlobalClientContactSchema, GlobalClientRegisterSchema
from src.schemas.globalClient.response import GlobalClientResponseSchema
from src.schemas.globalClient.update import GlobalClientUpdateSchema
from src.services.miniApp.miniApp_service import MiniAppService

router = APIRouter()

get_miniApp_service = make_service_dependency(MiniAppService)

@router.post(
    "/me",
    response_model = GlobalClientResponseSchema,
    status_code = status.HTTP_201_CREATED,
    summary = "Регистрация клиента",
    description = "Создает профиль клиента мини-приложения. Обязательны `firstname`, `lastname`, `sex` и `contact` — строка `response` из колбэка `WebApp.requestContact` (подписана Telegram так же, как `initData`); номер из нее сохраняется как `telegram_phone`. `call_phone` — необязательный номер для звонков, если отличается от номера Telegram. Без регистрации остальные эндпоинты мини-приложения отвечают `GLOBAL_CLIENT_NOT_REGISTERED`."
)
async def register(data: GlobalClientRegisterSchema,
                   user: dict = Depends(get_telegram_user),
                   miniAppService: MiniAppService = Depends(get_miniApp_service)):
    return await miniAppService.register(user, data)

@router.get(
    "/me",
    response_model = GlobalClientResponseSchema,
    status_code = status.HTTP_200_OK,
    summary = "Профиль клиента",
    description = "Профиль зарегистрированного клиента. Если клиент еще не зарегистрирован — `GLOBAL_CLIENT_NOT_REGISTERED` (404): мини-приложение показывает форму регистрации (`POST /me`)."
)
async def get_profile(client: GlobalClient = Depends(get_current_global_client),
                      miniAppService: MiniAppService = Depends(get_miniApp_service)):
    return await miniAppService.get_profile(client)

@router.patch(
    "/me",
    response_model = GlobalClientResponseSchema,
    status_code = status.HTTP_200_OK,
    summary = "Обновить профиль клиента",
    description = "Обновляет данные клиента. `firstname`, `lastname` и `sex` очистить нельзя (null игнорируется). `telegram_phone` здесь изменить нельзя — только через `POST /me/contact`. `call_phone` — необязательный номер для звонков, если отличается от номера Telegram."
)
async def update_profile(data: GlobalClientUpdateSchema,
                         client: GlobalClient = Depends(get_current_global_client),
                         miniAppService: MiniAppService = Depends(get_miniApp_service)):
    return await miniAppService.update_profile(client, data)

@router.post(
    "/me/contact",
    response_model = GlobalClientResponseSchema,
    status_code = status.HTTP_200_OK,
    summary = "Обновить номер телефона из Telegram",
    description = "Принимает строку `response` из колбэка `WebApp.requestContact` (подписана Telegram так же, как `initData`), проверяет подпись и сохраняет номер как `telegram_phone` — например, если клиент сменил номер. Номер может быть привязан только к одному аккаунту Telegram."
)
async def share_contact(data: GlobalClientContactSchema,
                        client: GlobalClient = Depends(get_current_global_client),
                        miniAppService: MiniAppService = Depends(get_miniApp_service)):
    return await miniAppService.share_contact(client, data)

@router.get(
    "/tenants",
    response_model = list[MiniAppTenantResponseSchema],
    status_code = status.HTTP_200_OK,
    summary = "Список организаций",
    description = "Организации (включая филиалы), в которые можно записаться: активные, с включенной записью через Telegram (`enable_telegram_booking`) и собственной активной подпиской.",
    dependencies = [Depends(get_current_global_client)]
)
async def get_tenants(miniAppService: MiniAppService = Depends(get_miniApp_service)):
    return await miniAppService.get_tenants()

@router.get(
    "/tenants/{tenant_id}/services",
    response_model = list[MiniAppServiceResponseSchema],
    status_code = status.HTTP_200_OK,
    summary = "Услуги организации",
    description = "Услуги, доступные для онлайн-записи: не в архиве, с указанной длительностью (`estimated_time`, минуты) и хотя бы одним активным сотрудником, который их оказывает. Сотрудники и их график клиенту не показываются.",
    dependencies = [Depends(get_current_global_client)]
)
async def get_services(tenant_id: int,
                       miniAppService: MiniAppService = Depends(get_miniApp_service)):
    return await miniAppService.get_services(tenant_id)

@router.post(
    "/appointment-requests",
    response_model = MiniAppAppointmentRequestResponseSchema,
    status_code = status.HTTP_201_CREATED,
    summary = "Создать заявку на запись",
    description = "Создает заявку на запись: услуги с количеством (`services`) и желаемое время начала (`start_time_est`, любое будущее время — график не проверяется). Время окончания — оценка по длительности услуг. Посещение создает сотрудник организации при подтверждении; если заявку не подтвердили за `time_to_confirm_booking` минут (или до желаемого времени), она отменяется автоматически. Ограничения: не более `max_pending_booking_requests` ожидающих заявок в одной организации (настройка организации) и не более `MINIAPP_MAX_PENDING_REQUESTS_TOTAL` во всех организациях."
)
async def create_request(data: AppointmentRequestCreateSchema,
                         client: GlobalClient = Depends(get_current_global_client),
                         miniAppService: MiniAppService = Depends(get_miniApp_service)):
    return await miniAppService.create_request(client, data)

@router.post(
    "/appointment-requests/get-all",
    response_model = PaginatedResponseSchema[MiniAppAppointmentRequestResponseSchema],
    status_code = status.HTTP_200_OK,
    summary = "Мои заявки на запись",
    description = "Заявки клиента во всех организациях, новые первыми. Для подтвержденных заявок `appointment_status` — текущий статус посещения."
)
async def get_requests(data: PaginationSchema,
                       client: GlobalClient = Depends(get_current_global_client),
                       miniAppService: MiniAppService = Depends(get_miniApp_service)):
    return await miniAppService.get_requests(client, data)

@router.patch(
    "/appointment-requests/cancel",
    response_model = MiniAppAppointmentRequestResponseSchema,
    status_code = status.HTTP_200_OK,
    summary = "Отменить заявку на запись",
    description = "Отменяет заявку в статусе `pending` или `confirmed` с необязательной причиной (`reason`). Для подтвержденной заявки сначала автоматически отменяется посещение — кроме завершенного, оплаченного или с активным чеком, — затем уведомляются сотрудники: администраторы, сотрудники с правом `APPOINTMENT_REQUESTS_READ` и назначенные на это посещение."
)
async def cancel_request(data: AppointmentRequestClientCancelSchema,
                         client: GlobalClient = Depends(get_current_global_client),
                         miniAppService: MiniAppService = Depends(get_miniApp_service)):
    return await miniAppService.cancel_request(client, data)
