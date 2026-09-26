import math
from datetime import datetime, timezone
from src.core.dependencies.context import get_current_tenant_id
from src.core.dependencies.uow import UnitOfWork
from src.exceptions.appointmentRequest_exceptions import (
    AppointmentRequestExpired, AppointmentRequestNotFound, AppointmentRequestNotPending,
    ClientLinkedToAnotherGlobalClient, GlobalClientAlreadyLinked)
from src.exceptions.client_exceptions import ClientIsArchived, ClientNotFound
from src.repository.appointment.appointment_model import AppointmentCreatedVia
from src.repository.appointment.appointmentRequest_model import AppointmentRequest, AppointmentRequestStatus
from src.repository.client.client_model import Client
from src.repository.globalClient.globalClient_model import GlobalClient
from src.schemas.appointment.create import AppointmentCreateSchema
from src.schemas.appointmentRequest.update import AppointmentRequestConfirmSchema, AppointmentRequestDeclineSchema
from src.schemas.base import RequestAllObject
from src.services.appointment.appointment_service import AppointmentService
from src.services.miniApp.clientNotifications import confirmed_text, declined_text, notify_telegram_client
from src.services.system.tenantLimits_service import TenantLimit, ensure_tenant_capacity

class AppointmentRequestService:
    """Organization (staff) side of Telegram booking: review, confirm or decline requests."""
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get_all(self, data: RequestAllObject) -> dict:
        items, total_items = await self.uow.appointmentRequests.get_all(data)
        total_pages = math.ceil(total_items / data.pageSize) if data.pageSize > 0 else 0
        return {
            "items": items,
            "page": data.page,
            "pageSize": data.pageSize,
            "totalItems": total_items,
            "totalPages": total_pages
        }

    async def get(self, id: int) -> AppointmentRequest:
        request = await self.uow.appointmentRequests.get(id)
        if request is None: raise AppointmentRequestNotFound(id)
        return request

    async def get_matching_clients(self, id: int) -> list[Client]:
        """Organization's clients this request's Telegram client may be - to pick `client_id` on confirm."""
        request = await self.get(id)
        global_client = request.global_client
        phones = [phone for phone in (global_client.telegram_phone, global_client.call_phone) if phone]
        return await self.uow.clients.find_matching_global_client(global_client.id, global_client.telegram_user_id, phones)

    async def confirm(self, data: AppointmentRequestConfirmSchema) -> AppointmentRequest:
        """Creates the appointment staff decided on (time, employees, services) and links it to the request."""
        request = await self._get_pending(data.id)
        telegram_user_id = request.global_client.telegram_user_id
        client = await self._resolve_client(request.global_client, data.client_id, data.new_client_phone)

        appointment = await AppointmentService(self.uow).create(
            AppointmentCreateSchema(
                client_id = client.id,
                start_time_est = data.start_time_est,
                end_time_est = data.end_time_est,
                records = data.records,
                notes = data.notes if data.notes is not None else request.comment,
            ),
            created_via = AppointmentCreatedVia.TELEGRAM,
        )

        request = await self.uow.appointmentRequests.update(
            request.id,
            status = AppointmentRequestStatus.CONFIRMED,
            appointment_id = appointment.id,
            decided_at = datetime.now(timezone.utc),
        )

        # Commit before telling the client: the request's own commit runs only after the response
        await self.uow.db.commit()
        tenant = await self.uow.tenants.get(id = request.tenant_id)
        notify_telegram_client(telegram_user_id, confirmed_text(tenant.name, appointment.start_time_est))
        return request

    async def decline(self, data: AppointmentRequestDeclineSchema) -> AppointmentRequest:
        request = await self._get_pending(data.id)
        telegram_user_id = request.global_client.telegram_user_id
        request = await self.uow.appointmentRequests.update(
            request.id,
            status = AppointmentRequestStatus.DECLINED,
            decline_reason = data.reason,
            decided_at = datetime.now(timezone.utc),
        )

        await self.uow.db.commit()
        tenant = await self.uow.tenants.get(id = request.tenant_id)
        notify_telegram_client(telegram_user_id, declined_text(tenant.name, request.start_time_est, data.reason))
        return request

    async def _get_pending(self, id: int) -> AppointmentRequest:
        request = await self.uow.appointmentRequests.get(id, lock = True)
        if request is None: raise AppointmentRequestNotFound(id)
        if request.status != AppointmentRequestStatus.PENDING: raise AppointmentRequestNotPending(id, request.status)
        # The expiry job runs once a minute - don't let a request past its time slip through meanwhile
        if request.expires_at <= datetime.now(timezone.utc): raise AppointmentRequestExpired(id)
        return request

    async def _resolve_client(self, global_client: GlobalClient, client_id: int | None,
                              new_client_phone: str | None) -> Client:
        """Organization's client for the Telegram client: the explicitly chosen one (linked now),
        the one linked earlier (by global client or Telegram user id), or a new one created
        from the Telegram profile - counted against the tenant's max_clients."""
        linked = await self.uow.clients.get_by_global_client(global_client.id) \
            or await self.uow.clients.get_by_telegram_user_id(global_client.telegram_user_id)

        if client_id is not None:
            if linked is not None and linked.id != client_id: raise GlobalClientAlreadyLinked(linked.id)
            client = await self.uow.clients.get(client_id)
            if client is None: raise ClientNotFound(client_id)
            if client.archived: raise ClientIsArchived(client.id, client.firstname)
            if client.global_client_id not in (None, global_client.id) \
                    or client.telegram_user_id not in (None, global_client.telegram_user_id):
                raise ClientLinkedToAnotherGlobalClient(client.id)
            return await self._link(client, global_client)

        if linked is not None:
            if linked.archived: raise ClientIsArchived(linked.id, linked.firstname)
            return await self._link(linked, global_client)

        await ensure_tenant_capacity(self.uow, get_current_tenant_id(), {TenantLimit.CLIENTS: 1})
        return await self.uow.clients.create(Client(
            firstname = global_client.firstname,
            lastname = global_client.lastname,
            middlename = global_client.middlename,
            phone = new_client_phone or global_client.call_phone or global_client.telegram_phone,
            birth_date = global_client.birth_date,
            sex = global_client.sex,
            global_client_id = global_client.id,
            telegram_user_id = global_client.telegram_user_id,
        ))

    async def _link(self, client: Client, global_client: GlobalClient) -> Client:
        """Stores both links on the tenant's client if either is missing."""
        if client.global_client_id == global_client.id and client.telegram_user_id == global_client.telegram_user_id:
            return client
        return await self.uow.clients.update(
            client.id, global_client_id = global_client.id, telegram_user_id = global_client.telegram_user_id)
