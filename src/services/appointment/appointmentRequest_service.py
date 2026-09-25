import math
from datetime import datetime, timezone
from decimal import Decimal
from src.core.dependencies.uow import UnitOfWork
from src.exceptions.appointmentRequest_exceptions import (
    AppointmentRequestExpired, AppointmentRequestNotFound, AppointmentRequestNotPending,
    AppointmentRequestServiceMissing, ClientLinkedToAnotherGlobalClient, GlobalClientAlreadyLinked)
from src.exceptions.client_exceptions import ClientIsArchived, ClientNotFound
from src.repository.appointment.appointment_model import AppointmentCreatedVia
from src.repository.appointment.appointmentRequest_model import AppointmentRequest, AppointmentRequestStatus
from src.repository.client.client_model import Client
from src.repository.globalClient.globalClient_model import GlobalClient
from src.schemas.appointment.create import AppointmentCreateSchema, AppointmentRecordsCreateOptionalSchema, AppointmentServicesCreateOptionalSchema
from src.schemas.appointmentRequest.update import AppointmentRequestConfirmSchema, AppointmentRequestDeclineSchema
from src.schemas.base import RequestAllObject
from src.services.appointment.appointment_service import AppointmentService

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
        phones = [phone for phone in (global_client.contact_phone, global_client.call_phone) if phone]
        return await self.uow.clients.find_matching_global_client(global_client.id, phones)

    async def confirm(self, data: AppointmentRequestConfirmSchema) -> AppointmentRequest:
        request = await self._get_pending(data.id)
        if request.service_id is None: raise AppointmentRequestServiceMissing(request.id)

        client = await self._resolve_client(request.global_client, data.client_id)

        # Honor the price the client saw when requesting, if it has changed since
        price, price_changed_reason = None, None
        service = await self.uow.services.get(request.service_id)
        snapshot_price = Decimal(request.service_snapshot["price"])
        if service is not None and snapshot_price != service.price and snapshot_price >= 1:
            price, price_changed_reason = snapshot_price, "Цена на момент заявки из Telegram"

        appointment = await AppointmentService(self.uow).create(
            AppointmentCreateSchema(
                client_id = client.id,
                start_time_est = request.start_time_est.astimezone(timezone.utc),
                end_time_est = request.end_time_est.astimezone(timezone.utc),
                records = [AppointmentRecordsCreateOptionalSchema(
                    employee_id = data.employee_id,
                    services = [AppointmentServicesCreateOptionalSchema(
                        service_id = request.service_id,
                        price = price,
                        price_changed_reason = price_changed_reason,
                    )],
                )],
                notes = request.comment,
            ),
            created_via = AppointmentCreatedVia.TELEGRAM,
        )

        return await self.uow.appointmentRequests.update(
            request.id,
            status = AppointmentRequestStatus.CONFIRMED,
            appointment_id = appointment.id,
            decided_at = datetime.now(timezone.utc),
        )

    async def decline(self, data: AppointmentRequestDeclineSchema) -> AppointmentRequest:
        request = await self._get_pending(data.id)
        return await self.uow.appointmentRequests.update(
            request.id,
            status = AppointmentRequestStatus.DECLINED,
            decline_reason = data.reason,
            decided_at = datetime.now(timezone.utc),
        )

    async def _get_pending(self, id: int) -> AppointmentRequest:
        request = await self.uow.appointmentRequests.get(id, lock = True)
        if request is None: raise AppointmentRequestNotFound(id)
        if request.status != AppointmentRequestStatus.PENDING: raise AppointmentRequestNotPending(id, request.status)
        # The expiry job runs once a minute - don't let a request past its time slip through meanwhile
        if request.expires_at <= datetime.now(timezone.utc): raise AppointmentRequestExpired(id)
        return request

    async def _resolve_client(self, global_client: GlobalClient, client_id: int | None) -> Client:
        """Organization's client for the Telegram client: the explicitly chosen one (linked now),
        the one linked on an earlier confirm, or a new one created from the Telegram profile."""
        linked = await self.uow.clients.get_by_global_client(global_client.id)

        if client_id is not None:
            if linked is not None and linked.id != client_id: raise GlobalClientAlreadyLinked(linked.id)
            client = await self.uow.clients.get(client_id)
            if client is None: raise ClientNotFound(client_id)
            if client.archived: raise ClientIsArchived(client.id, client.firstname)
            if client.global_client_id is None:
                client = await self.uow.clients.update(client.id, global_client_id = global_client.id)
            elif client.global_client_id != global_client.id:
                raise ClientLinkedToAnotherGlobalClient(client.id)
            return client

        if linked is not None:
            if linked.archived: raise ClientIsArchived(linked.id, linked.firstname)
            return linked

        return await self.uow.clients.create(Client(
            firstname = global_client.firstname,
            lastname = global_client.lastname,
            middlename = global_client.middlename,
            phone = global_client.call_phone or global_client.contact_phone,
            birth_date = global_client.birth_date,
            sex = global_client.sex,
            global_client_id = global_client.id,
        ))
