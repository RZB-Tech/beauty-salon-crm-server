from datetime import date
from fastapi import APIRouter, Depends, Query, status
from src.core.dependencies.miniApp import get_current_global_client
from src.core.dependencies.uow import make_service_dependency
from src.repository.globalClient.globalClient_model import GlobalClient
from src.schemas.appointmentRequest.create import AppointmentRequestCreateSchema
from src.schemas.appointmentRequest.response import (
    BookingSlotSchema, MiniAppAppointmentRequestResponseSchema, MiniAppServiceResponseSchema, MiniAppTenantResponseSchema)
from src.schemas.appointmentRequest.update import AppointmentRequestClientCancelSchema
from src.schemas.base import PaginatedResponseSchema, PaginationSchema
from src.schemas.globalClient.create import GlobalClientContactSchema
from src.schemas.globalClient.response import GlobalClientResponseSchema
from src.schemas.globalClient.update import GlobalClientUpdateSchema
from src.services.miniApp.miniApp_service import MiniAppService

router = APIRouter()

get_miniApp_service = make_service_dependency(MiniAppService)

@router.get(
    "/me",
    response_model = GlobalClientResponseSchema,
    status_code = status.HTTP_200_OK,
    summary = "Профиль клиента",
    description = "Возвращает профиль клиента мини-приложения. Клиент регистрируется автоматически при первом запросе с валидным `initData`. `is_profile_complete` — заполнены ли поля, обязательные для заявки на запись (`firstname`, `sex`, `contact_phone`)."
)
async def get_profile(client: GlobalClient = Depends(get_current_global_client),
                      miniAppService: MiniAppService = Depends(get_miniApp_service)):
    return await miniAppService.get_profile(client)

@router.patch(
    "/me",
    response_model = GlobalClientResponseSchema,
    status_code = status.HTTP_200_OK,
    summary = "Обновить профиль клиента",
    description = "Обновляет данные клиента. `contact_phone` здесь изменить нельзя — только через `POST /me/contact` (номер из Telegram). `call_phone` — необязательный номер для звонков, если отличается от номера Telegram."
)
async def update_profile(data: GlobalClientUpdateSchema,
                         client: GlobalClient = Depends(get_current_global_client),
                         miniAppService: MiniAppService = Depends(get_miniApp_service)):
    return await miniAppService.update_profile(client, data)

@router.post(
    "/me/contact",
    response_model = GlobalClientResponseSchema,
    status_code = status.HTTP_200_OK,
    summary = "Сохранить номер телефона из Telegram",
    description = "Принимает строку `response` из колбэка `WebApp.requestContact` (подписана Telegram так же, как `initData`), проверяет подпись и сохраняет номер как `contact_phone`. Номер может быть привязан только к одному аккаунту Telegram."
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
    description = "Активные организации (включая филиалы), у которых включена запись через Telegram (`enable_telegram_booking`).",
    dependencies = [Depends(get_current_global_client)]
)
async def get_tenants(miniAppService: MiniAppService = Depends(get_miniApp_service)):
    return await miniAppService.get_tenants()

@router.get(
    "/tenants/{tenant_id}/services",
    response_model = list[MiniAppServiceResponseSchema],
    status_code = status.HTTP_200_OK,
    summary = "Услуги организации",
    description = "Услуги, доступные для онлайн-записи: не в архиве, с указанной длительностью (`estimated_time`, минуты) и хотя бы одним активным сотрудником, который их оказывает.",
    dependencies = [Depends(get_current_global_client)]
)
async def get_services(tenant_id: int,
                       miniAppService: MiniAppService = Depends(get_miniApp_service)):
    return await miniAppService.get_services(tenant_id)

@router.get(
    "/tenants/{tenant_id}/services/{service_id}/slots",
    response_model = list[BookingSlotSchema],
    status_code = status.HTTP_200_OK,
    summary = "Свободное время для записи",
    description = "Свободные слоты на дату `date` (UTC) с шагом `booking_slot_step` из настроек организации. Слот свободен, если хотя бы один сотрудник, оказывающий услугу, работает и не занят в это время; ожидающие заявки на эту же услугу занимают по одному сотруднику.",
    dependencies = [Depends(get_current_global_client)]
)
async def get_slots(tenant_id: int, service_id: int,
                    day: date = Query(alias = "date"),
                    miniAppService: MiniAppService = Depends(get_miniApp_service)):
    return await miniAppService.get_slots(tenant_id, service_id, day)

@router.post(
    "/appointment-requests",
    response_model = MiniAppAppointmentRequestResponseSchema,
    status_code = status.HTTP_201_CREATED,
    summary = "Создать заявку на запись",
    description = "Создает заявку на запись в организацию. Посещение создается только после подтверждения сотрудником организации; если заявку не подтвердили за `time_to_confirm_booking` минут (или до начала записи), она отменяется автоматически."
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
    description = "Отменяет заявку в статусе `pending` или `confirmed`. Для подтвержденной заявки отменяется и посещение — кроме завершенного, оплаченного или с активным чеком."
)
async def cancel_request(data: AppointmentRequestClientCancelSchema,
                         client: GlobalClient = Depends(get_current_global_client),
                         miniAppService: MiniAppService = Depends(get_miniApp_service)):
    return await miniAppService.cancel_request(client, data.id)
