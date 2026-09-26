import math
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from sqlalchemy import func, select
from src.core.auth.telegram import normalize_phone, parse_json_field, validate_telegram_signed_data
from src.core.config import settings
from src.core.dependencies.auth import has_active_subscription, is_tenant_admin_active
from src.core.dependencies.context import tenant_context
from src.core.dependencies.uow import UnitOfWork
from src.core.permissions import PermissionCode, compute_effective_permissions, has_permission
from src.database.base import ActorType
from src.exceptions.appointmentRequest_exceptions import (
    AppointmentIsFinished, AppointmentRequestCannotBeCancelled, AppointmentRequestNotFound, BookingTimeInPast,
    ClientAppointmentRequestConflict, ContactNotOwnedByUser, ContactPhoneAlreadyUsed, GlobalClientAlreadyRegistered,
    ServiceNotBookable, TenantBookingUnavailable, TooManyPendingAppointmentRequests)
from src.exceptions.auth_exceptions import TelegramAuthInvalid
from src.exceptions.service_exceptions import ServiceIsArchived, ServiceNotFound
from src.repository.appointment.appointment_model import AppointmentCancelledReason, AppointmentStatus
from src.repository.appointment.appointmentRequest_model import AppointmentRequest, AppointmentRequestCancelledReason, AppointmentRequestStatus
from src.repository.globalClient.globalClient_model import GlobalClient
from src.repository.notification.notification_model import Notification, NotificationType
from src.repository.service.service_model import Service
from src.repository.staff.staff_model import StaffType
from src.repository.tenant.tenant_model import Tenant
from src.schemas.appointment.update import AppointmentCancelSchema
from src.schemas.appointmentRequest.create import AppointmentRequestCreateSchema
from src.schemas.appointmentRequest.response import MiniAppAppointmentRequestResponseSchema
from src.schemas.appointmentRequest.update import AppointmentRequestClientCancelSchema
from src.schemas.base import PaginationSchema
from src.schemas.globalClient.create import GlobalClientContactSchema, GlobalClientRegisterSchema
from src.schemas.globalClient.update import GlobalClientUpdateSchema
from src.schemas.tenant.base import TenantPreferencesSchema
from src.services.appointment.appointment_service import AppointmentService
from src.services.system.tenantPreferences_service import load_tenant_preferences

# Advisory lock namespace (first key) for one client's request creation - see create_request
_CLIENT_REQUEST_LOCK = 10

class MiniAppService:
    """Client (global client) side of Telegram booking. Every tenant-scoped read/write runs
    inside tenant_context() so the tenant filter and audit listener work as for staff."""
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    # --- Registration / profile ---

    async def register(self, telegram_user: dict, data: GlobalClientRegisterSchema) -> GlobalClient:
        """Creates the client's profile - the only way a global_clients row appears."""
        telegram_user_id = telegram_user["id"]
        if await self.uow.globalClients.get_by_telegram_user_id(telegram_user_id) is not None:
            raise GlobalClientAlreadyRegistered()

        phone = await self._verified_phone(data.contact, telegram_user_id, client_id = None)
        return await self.uow.globalClients.create(GlobalClient(
            telegram_user_id = telegram_user_id,
            telegram_username = telegram_user.get("username"),
            telegram_phone = phone,
            call_phone = data.call_phone,
            firstname = data.firstname,
            lastname = data.lastname,
            middlename = data.middlename,
            birth_date = data.birth_date,
            sex = data.sex,
        ))

    async def get_profile(self, client: GlobalClient) -> GlobalClient:
        return client

    async def update_profile(self, client: GlobalClient, data: GlobalClientUpdateSchema) -> GlobalClient:
        fields = data.model_dump(exclude_unset = True)
        for required in ("firstname", "lastname", "sex"): # can't be cleared
            if fields.get(required) is None: fields.pop(required, None)
        return await self.uow.globalClients.update(client.id, **fields)

    async def share_contact(self, client: GlobalClient, data: GlobalClientContactSchema) -> GlobalClient:
        """Replaces the verified Telegram phone, e.g. after the client changed their number."""
        phone = await self._verified_phone(data.response, client.telegram_user_id, client_id = client.id)
        return await self.uow.globalClients.update(client.id, telegram_phone = phone)

    async def _verified_phone(self, signed_contact: str, telegram_user_id: int, client_id: int | None) -> str:
        """Phone from WebApp.requestContact's signed response - it must be the current user's
        own contact and not already belong to another client."""
        try:
            fields = validate_telegram_signed_data(
                signed_contact, settings.TELEGRAM_MINIAPP_BOT_TOKEN, settings.TELEGRAM_INIT_DATA_EXPIRE_SECONDS)
            contact = parse_json_field(fields, "contact")
        except ValueError:
            raise TelegramAuthInvalid()

        if contact.get("user_id") != telegram_user_id: raise ContactNotOwnedByUser()
        if not contact.get("phone_number"): raise TelegramAuthInvalid()

        phone = normalize_phone(contact["phone_number"])
        owner = await self.uow.globalClients.get_by_telegram_phone(phone)
        if owner is not None and owner.id != client_id: raise ContactPhoneAlreadyUsed()
        return phone

    # --- Catalog ---

    async def get_tenants(self) -> list[Tenant]:
        return await self.uow.tenants.get_all_bookable()

    async def get_services(self, tenant_id: int) -> list[Service]:
        await self._ensure_bookable(tenant_id)
        with tenant_context(tenant_id, None):
            return await self.uow.services.get_bookable()

    # --- Appointment requests ---

    async def create_request(self, client: GlobalClient, data: AppointmentRequestCreateSchema) -> MiniAppAppointmentRequestResponseSchema:
        preferences = await self._ensure_bookable(data.tenant_id)
        now = datetime.now(timezone.utc)
        if data.start_time_est <= now: raise BookingTimeInPast()

        # One request at a time per client, held until commit, so parallel requests
        # can't all pass the anti-spam counts below
        await self.uow.db.execute(select(func.pg_advisory_xact_lock(_CLIENT_REQUEST_LOCK, client.id)))

        total = await self.uow.appointmentRequests.count_pending_for_global_client(client.id)
        if total >= settings.MINIAPP_MAX_PENDING_REQUESTS_TOTAL:
            raise TooManyPendingAppointmentRequests(settings.MINIAPP_MAX_PENDING_REQUESTS_TOTAL, "total")
        at_tenant = await self.uow.appointmentRequests.count_pending_for_global_client(client.id, data.tenant_id)
        if at_tenant >= preferences.max_pending_booking_requests:
            raise TooManyPendingAppointmentRequests(preferences.max_pending_booking_requests, "tenant")

        async with self._as_tenant(data.tenant_id):
            services = []
            for item in data.services:
                service = await self._get_bookable_service(item.service_id)
                services.append({
                    "service_id": service.id,
                    "name": service.name,
                    "price": str(service.price),
                    "estimated_time": service.estimated_time,
                    "quantity": item.quantity,
                })

            start = data.start_time_est
            end = start + timedelta(minutes = sum(s["estimated_time"] * s["quantity"] for s in services))
            if await self.uow.appointmentRequests.global_client_has_overlap(client.id, start, end):
                raise ClientAppointmentRequestConflict()

            request = await self.uow.appointmentRequests.create(AppointmentRequest(
                global_client_id = client.id,
                services = services,
                start_time_est = start,
                end_time_est = end,
                comment = data.comment,
                expires_at = min(now + timedelta(minutes = preferences.time_to_confirm_booking), start),
            ))
            await self._notify_staff(request, client)

        tenant = await self.uow.tenants.get(id = data.tenant_id)
        return self._to_response(request, tenant.name)

    async def get_requests(self, client: GlobalClient, data: PaginationSchema) -> dict:
        rows, total_items = await self.uow.appointmentRequests.get_all_for_global_client(client.id, data)
        return {
            "items": [self._to_response(request, tenant_name) for request, tenant_name in rows],
            "page": data.page,
            "pageSize": data.pageSize,
            "totalItems": total_items,
            "totalPages": math.ceil(total_items / data.pageSize) if data.pageSize > 0 else 0
        }

    async def cancel_request(self, client: GlobalClient, data: AppointmentRequestClientCancelSchema) -> MiniAppAppointmentRequestResponseSchema:
        request = await self.uow.appointmentRequests.get_for_global_client(client.id, data.id, lock = True)
        if request is None: raise AppointmentRequestNotFound(data.id)
        if request.status not in (AppointmentRequestStatus.PENDING, AppointmentRequestStatus.CONFIRMED):
            raise AppointmentRequestCannotBeCancelled(data.id, request.status)

        async with self._as_tenant(request.tenant_id):
            if request.status == AppointmentRequestStatus.CONFIRMED and request.appointment_id is not None:
                appointment = await self.uow.appointments.get(request.appointment_id)
                # Already cancelled by the organization - only the request is left to cancel
                if appointment is not None and appointment.status != AppointmentStatus.CANCELLED:
                    if appointment.status == AppointmentStatus.FINISHED: raise AppointmentIsFinished(appointment.id)
                    await AppointmentService(self.uow).cancel(AppointmentCancelSchema(
                        id = appointment.id, reason = AppointmentCancelledReason.CLIENT_CANCELLED))

            request = await self.uow.appointmentRequests.update(
                request.id,
                status = AppointmentRequestStatus.CANCELLED,
                cancelled_reason = AppointmentRequestCancelledReason.CLIENT_CANCELLED,
                cancel_comment = data.reason,
                decided_at = datetime.now(timezone.utc),
            )

        tenant = await self.uow.tenants.get(id = request.tenant_id)
        return self._to_response(request, tenant.name)

    # --- Helpers ---

    @asynccontextmanager
    async def _as_tenant(self, tenant_id: int):
        """Acts as the tenant's Telegram actor (created on first use) - for writes."""
        with tenant_context(tenant_id, None):
            actor = await self.uow.staffs.get_or_create_actor(tenant_id, ActorType.TELEGRAM, "Telegram booking")
        with tenant_context(tenant_id, actor.id):
            yield

    async def _ensure_bookable(self, tenant_id: int) -> TenantPreferencesSchema:
        """
        Clients can book at a tenant only if it's enabled, has Telegram booking on and
        has its OWN active subscription (a branch's own, never its parent's) - otherwise
        nobody there could log in to confirm. All three are cache-first.
        """
        if not await is_tenant_admin_active(tenant_id): raise TenantBookingUnavailable(tenant_id)
        preferences = await load_tenant_preferences(self.uow, tenant_id)
        if preferences is None or not preferences.enable_telegram_booking: raise TenantBookingUnavailable(tenant_id)
        if not await has_active_subscription(tenant_id): raise TenantBookingUnavailable(tenant_id)
        return preferences

    async def _get_bookable_service(self, service_id: int) -> Service:
        """Same rules as the catalog (ServiceRepository.get_bookable)."""
        service = await self.uow.services.get_with_employees(service_id)
        if service is None: raise ServiceNotFound(service_id)
        if service.archived: raise ServiceIsArchived(service.id, service.name)
        has_employee = any(e.active and not e.archived for e in service.employees)
        if service.estimated_time <= 0 or not has_employee: raise ServiceNotBookable(service.id, service.name)
        return service

    async def _notify_staff(self, request: AppointmentRequest, client: GlobalClient) -> None:
        """'Action required' notification to every active staff who can see appointment requests."""
        recipients = [
            staff for staff in await self.uow.staffs.get_active_with_roles()
            if staff.staff_type == StaffType.ADMIN
            or has_permission(set(compute_effective_permissions(staff)), PermissionCode.APPOINTMENT_REQUESTS_READ)
        ]
        phones = ", ".join(phone for phone in (client.telegram_phone, client.call_phone) if phone)
        services = "; ".join(f"{s['name']} × {s['quantity']}" for s in request.services)
        body = (
            f"Требуется действие: подтвердите или отклоните заявку на запись. Источник: Telegram.\n"
            f"Клиент: {client.firstname} {client.lastname}, {phones}\n"
            f"Услуги: {services}\n"
            f"Желаемое время: {request.start_time_est:%d.%m.%Y %H:%M} (UTC)"
        )
        now = datetime.now(timezone.utc)
        for staff in recipients:
            await self.uow.notifications.create(Notification(
                title = "Новая заявка на запись (Telegram)",
                body = body,
                type = NotificationType.APPOINTMENT_REQUEST,
                scheduled_at = now,
                recipient_staff_id = staff.id,
                appointment_request_id = request.id,
            ))

    @staticmethod
    def _to_response(request: AppointmentRequest, tenant_name: str) -> MiniAppAppointmentRequestResponseSchema:
        return MiniAppAppointmentRequestResponseSchema(
            id = request.id,
            tenant_id = request.tenant_id,
            tenant_name = tenant_name,
            services = request.services,
            start_time_est = request.start_time_est,
            end_time_est = request.end_time_est,
            comment = request.comment,
            status = request.status,
            cancelled_reason = request.cancelled_reason,
            cancel_comment = request.cancel_comment,
            decline_reason = request.decline_reason,
            expires_at = request.expires_at,
            decided_at = request.decided_at,
            appointment_id = request.appointment_id,
            appointment_status = request.appointment.status if request.appointment is not None else None,
            created_at = request.created_at,
        )
