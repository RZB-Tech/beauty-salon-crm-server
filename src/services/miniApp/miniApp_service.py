import math
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from src.core.auth.telegram import normalize_phone, parse_json_field, validate_telegram_signed_data
from src.core.config import settings
from src.core.dependencies.context import tenant_context
from src.core.dependencies.uow import UnitOfWork
from src.core.permissions import PermissionCode, compute_effective_permissions, has_permission
from src.database.base import ActorType
from src.exceptions.appointmentRequest_exceptions import (
    AppointmentIsFinished, AppointmentRequestCannotBeCancelled, AppointmentRequestNotFound, BookingSlotUnavailable,
    BookingTimeInPast, ClientAppointmentRequestConflict, ContactNotOwnedByUser, ContactPhoneAlreadyUsed,
    GlobalClientProfileIncomplete, ServiceNotBookable, TenantBookingUnavailable, TooManyPendingAppointmentRequests)
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
from src.schemas.appointmentRequest.response import BookingSlotSchema, MiniAppAppointmentRequestResponseSchema
from src.schemas.base import PaginationSchema
from src.schemas.globalClient.create import GlobalClientContactSchema
from src.schemas.globalClient.update import GlobalClientUpdateSchema
from src.schemas.tenant.base import TenantPreferencesSchema
from src.services.appointment.appointment_service import AppointmentService

@dataclass
class _DayAvailability:
    """Everything needed to tell whether a service can be booked at some time of one day."""
    duration: timedelta
    # employee_id -> working windows of that day
    windows: dict[int, list[tuple[datetime, datetime]]] = field(default_factory = dict)
    # employee_id -> intervals taken by appointments
    busy: dict[int, list[tuple[datetime, datetime]]] = field(default_factory = dict)
    # pending requests for the same service - each soft-holds one employee
    pending: list[tuple[datetime, datetime]] = field(default_factory = list)

    def is_available(self, start: datetime) -> bool:
        end = start + self.duration
        free_employees = sum(
            1 for employee_id, windows in self.windows.items()
            if any(w_start <= start and end <= w_end for w_start, w_end in windows)
            and not any(b_start < end and start < b_end for b_start, b_end in self.busy.get(employee_id, []))
        )
        held = sum(1 for p_start, p_end in self.pending if p_start < end and start < p_end)
        return free_employees > held

class MiniAppService:
    """Client (global client) side of Telegram booking. Every tenant-scoped read/write runs
    inside tenant_context() so the tenant filter and audit listener work as for staff."""
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    # --- Profile ---

    async def get_profile(self, client: GlobalClient) -> GlobalClient:
        return client

    async def update_profile(self, client: GlobalClient, data: GlobalClientUpdateSchema) -> GlobalClient:
        fields = data.model_dump(exclude_unset = True)
        if fields.get("firstname") is None: fields.pop("firstname", None) # required, can't be cleared
        return await self.uow.globalClients.update(client.id, **fields)

    async def share_contact(self, client: GlobalClient, data: GlobalClientContactSchema) -> GlobalClient:
        try:
            fields = validate_telegram_signed_data(
                data.response, settings.TELEGRAM_MINIAPP_BOT_TOKEN, settings.TELEGRAM_INIT_DATA_EXPIRE_SECONDS)
            contact = parse_json_field(fields, "contact")
        except ValueError:
            raise TelegramAuthInvalid()

        if contact.get("user_id") != client.telegram_user_id: raise ContactNotOwnedByUser()
        if not contact.get("phone_number"): raise TelegramAuthInvalid()

        phone = normalize_phone(contact["phone_number"])
        owner = await self.uow.globalClients.get_by_contact_phone(phone)
        if owner is not None and owner.id != client.id: raise ContactPhoneAlreadyUsed()

        return await self.uow.globalClients.update(client.id, contact_phone = phone)

    # --- Catalog ---

    async def get_tenants(self) -> list[Tenant]:
        return await self.uow.tenants.get_all_bookable()

    async def get_services(self, tenant_id: int) -> list[Service]:
        await self._get_bookable_tenant(tenant_id)
        async with self._as_tenant(tenant_id):
            return await self.uow.services.get_bookable()

    async def get_slots(self, tenant_id: int, service_id: int, day: date) -> list[BookingSlotSchema]:
        _, preferences = await self._get_bookable_tenant(tenant_id)
        now = datetime.now(timezone.utc)
        if day < now.date(): return []

        async with self._as_tenant(tenant_id):
            service = await self._get_bookable_service(service_id)
            availability = await self._load_day_availability(service, day)

        step = timedelta(minutes = preferences.booking_slot_step)
        day_start = datetime.combine(day, time.min, tzinfo = timezone.utc)
        slots = []
        start = day_start
        while start + availability.duration <= day_start + timedelta(days = 1):
            if start > now and availability.is_available(start):
                slots.append(BookingSlotSchema(start_time_est = start, end_time_est = start + availability.duration))
            start += step
        return slots

    # --- Appointment requests ---

    async def create_request(self, client: GlobalClient, data: AppointmentRequestCreateSchema) -> MiniAppAppointmentRequestResponseSchema:
        missing = [name for name in ("firstname", "sex", "contact_phone") if not getattr(client, name)]
        if missing: raise GlobalClientProfileIncomplete(missing)

        tenant, preferences = await self._get_bookable_tenant(data.tenant_id)
        now = datetime.now(timezone.utc)
        if data.start_time_est <= now: raise BookingTimeInPast()

        async with self._as_tenant(tenant.id):
            service = await self._get_bookable_service(data.service_id)
            start = data.start_time_est
            end = start + timedelta(minutes = service.estimated_time)

            pending = await self.uow.appointmentRequests.count_pending_for_global_client(client.id, tenant.id)
            if pending >= settings.MINIAPP_MAX_PENDING_REQUESTS_PER_TENANT:
                raise TooManyPendingAppointmentRequests(settings.MINIAPP_MAX_PENDING_REQUESTS_PER_TENANT)

            if await self.uow.appointmentRequests.global_client_has_overlap(client.id, start, end):
                raise ClientAppointmentRequestConflict()

            availability = await self._load_day_availability(service, start.date())
            if start.date() != end.date() or not availability.is_available(start):
                raise BookingSlotUnavailable()

            request = await self.uow.appointmentRequests.create(AppointmentRequest(
                global_client_id = client.id,
                service_id = service.id,
                service_snapshot = {
                    "service_id": service.id,
                    "name": service.name,
                    "price": str(service.price),
                    "estimated_time": service.estimated_time,
                },
                start_time_est = start,
                end_time_est = end,
                comment = data.comment,
                expires_at = min(now + timedelta(minutes = preferences.time_to_confirm_booking), start),
            ))
            await self._notify_staff(request, client, service)

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

    async def cancel_request(self, client: GlobalClient, id: int) -> MiniAppAppointmentRequestResponseSchema:
        request = await self.uow.appointmentRequests.get_for_global_client(client.id, id, lock = True)
        if request is None: raise AppointmentRequestNotFound(id)
        if request.status not in (AppointmentRequestStatus.PENDING, AppointmentRequestStatus.CONFIRMED):
            raise AppointmentRequestCannotBeCancelled(id, request.status)

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
                decided_at = datetime.now(timezone.utc),
            )

        tenant = await self.uow.tenants.get(id = request.tenant_id)
        return self._to_response(request, tenant.name)

    # --- Helpers ---

    @asynccontextmanager
    async def _as_tenant(self, tenant_id: int):
        """Acts as the tenant's Telegram actor (created on first use)."""
        with tenant_context(tenant_id, None):
            actor = await self.uow.staffs.get_or_create_actor(tenant_id, ActorType.TELEGRAM, "Telegram booking")
        with tenant_context(tenant_id, actor.id):
            yield

    async def _get_bookable_tenant(self, tenant_id: int) -> tuple[Tenant, TenantPreferencesSchema]:
        tenant = await self.uow.tenants.get(id = tenant_id)
        if tenant is None or not tenant.active: raise TenantBookingUnavailable(tenant_id)
        preferences = TenantPreferencesSchema(**(tenant.preferences or {}))
        if not preferences.enable_telegram_booking: raise TenantBookingUnavailable(tenant_id)
        return tenant, preferences

    async def _get_bookable_service(self, service_id: int) -> Service:
        service = await self.uow.services.get_with_employees(service_id)
        if service is None: raise ServiceNotFound(service_id)
        if service.archived: raise ServiceIsArchived(service.id, service.name)
        if service.estimated_time <= 0: raise ServiceNotBookable(service.id, service.name)
        return service

    async def _load_day_availability(self, service: Service, day: date) -> _DayAvailability:
        availability = _DayAvailability(duration = timedelta(minutes = service.estimated_time))
        employee_ids = [e.id for e in service.employees if e.active and not e.archived]
        if not employee_ids: return availability

        # Work schedules are stored as times of day; the backend treats every tenant as UTC
        for schedule in await self.uow.work_schedules.get_day_schedules(employee_ids, day):
            availability.windows.setdefault(schedule.employee_id, []).append((
                datetime.combine(day, schedule.start_time, tzinfo = timezone.utc),
                datetime.combine(day, schedule.end_time, tzinfo = timezone.utc),
            ))

        day_start = datetime.combine(day, time.min, tzinfo = timezone.utc)
        day_end = day_start + timedelta(days = 1)
        for employee_id, start, end in await self.uow.appointmentRecords.get_busy_intervals(employee_ids, day_start, day_end):
            availability.busy.setdefault(employee_id, []).append((start, end))

        availability.pending = [
            (request.start_time_est, request.end_time_est)
            for request in await self.uow.appointmentRequests.get_pending_between(day_start, day_end)
            if request.service_id == service.id
        ]
        return availability

    async def _notify_staff(self, request: AppointmentRequest, client: GlobalClient, service: Service) -> None:
        """'Action required' notification to every active staff who can see appointment requests."""
        recipients = [
            staff for staff in await self.uow.staffs.get_active_with_roles()
            if staff.staff_type == StaffType.ADMIN
            or has_permission(set(compute_effective_permissions(staff)), PermissionCode.APPOINTMENT_REQUESTS_READ)
        ]
        full_name = " ".join(part for part in (client.firstname, client.lastname) if part)
        body = (
            f"Требуется действие: подтвердите или отклоните заявку на запись. Источник: Telegram.\n"
            f"Клиент: {full_name}, {client.call_phone or client.contact_phone}\n"
            f"Услуга: {service.name}\n"
            f"Время: {request.start_time_est:%d.%m.%Y %H:%M} – {request.end_time_est:%H:%M} (UTC)"
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
            service_snapshot = request.service_snapshot,
            start_time_est = request.start_time_est,
            end_time_est = request.end_time_est,
            comment = request.comment,
            status = request.status,
            cancelled_reason = request.cancelled_reason,
            decline_reason = request.decline_reason,
            expires_at = request.expires_at,
            decided_at = request.decided_at,
            appointment_id = request.appointment_id,
            appointment_status = request.appointment.status if request.appointment is not None else None,
            created_at = request.created_at,
        )
