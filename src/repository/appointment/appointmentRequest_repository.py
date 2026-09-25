from datetime import datetime

from sqlalchemy import and_, func, or_, select, update
from src.core.utils.model_filter import apply_dynamic_filters
from src.database.base import BaseRepository
from src.repository.appointment.appointment_model import Appointment, AppointmentStatus
from src.repository.appointment.appointmentRequest_model import AppointmentRequest, AppointmentRequestCancelledReason, AppointmentRequestStatus
from src.repository.tenant.tenant_model import Tenant
from src.schemas.base import PaginationSchema, RequestAllObject

class AppointmentRequestRepository(BaseRepository[AppointmentRequest]):
    async def create(self, appointmentRequest: AppointmentRequest) -> AppointmentRequest:
        self.db.add(appointmentRequest)
        await self.db.flush()
        await self.db.refresh(appointmentRequest)
        return appointmentRequest

    async def get_all(self, data: RequestAllObject) -> tuple[list[AppointmentRequest], int]:
        count_stmt = select(func.count()).select_from(AppointmentRequest)
        stmt = select(AppointmentRequest)
        count_stmt = apply_dynamic_filters(count_stmt, AppointmentRequest, data.filters)
        stmt = apply_dynamic_filters(stmt, AppointmentRequest, data.filters)
        total_items = await self.db.scalar(count_stmt) or 0
        offset_value = (data.page - 1) * data.pageSize
        stmt = stmt.order_by(AppointmentRequest.id.desc()).offset(offset_value).limit(data.pageSize)
        result = await self.db.execute(stmt)
        return result.scalars().all(), total_items

    async def get_pending_between(self, start: datetime, end: datetime) -> list[AppointmentRequest]:
        """Pending requests of the current tenant overlapping [start, end)."""
        result = await self.db.execute(
            select(AppointmentRequest).where(
                AppointmentRequest.status == AppointmentRequestStatus.PENDING,
                AppointmentRequest.start_time_est < end,
                AppointmentRequest.end_time_est > start,
            )
        )
        return list(result.scalars().all())

    # --- Global client (mini app) side: cross-tenant, always scoped by global_client_id ---

    async def get_for_global_client(self, global_client_id: int, id: int, lock: bool = False) -> AppointmentRequest | None:
        stmt = (
            select(AppointmentRequest)
            .where(AppointmentRequest.id == id, AppointmentRequest.global_client_id == global_client_id)
            .execution_options(skip_tenant_filter = True)
        )
        if lock: stmt = stmt.with_for_update(of = AppointmentRequest)
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_all_for_global_client(self, global_client_id: int,
                                        data: PaginationSchema) -> tuple[list[tuple[AppointmentRequest, str]], int]:
        """Returns (request, tenant name) pairs, newest first."""
        total_items = await self.db.scalar(
            select(func.count())
            .select_from(AppointmentRequest)
            .where(AppointmentRequest.global_client_id == global_client_id)
            .execution_options(skip_tenant_filter = True)
        ) or 0
        result = await self.db.execute(
            select(AppointmentRequest, Tenant.name)
            .join(Tenant, Tenant.id == AppointmentRequest.tenant_id)
            .where(AppointmentRequest.global_client_id == global_client_id)
            .order_by(AppointmentRequest.id.desc())
            .offset((data.page - 1) * data.pageSize)
            .limit(data.pageSize)
            .execution_options(skip_tenant_filter = True)
        )
        return [(row[0], row[1]) for row in result.unique().all()], total_items

    async def count_pending_for_global_client(self, global_client_id: int, tenant_id: int) -> int:
        return await self.db.scalar(
            select(func.count())
            .select_from(AppointmentRequest)
            .where(
                AppointmentRequest.global_client_id == global_client_id,
                AppointmentRequest.tenant_id == tenant_id,
                AppointmentRequest.status == AppointmentRequestStatus.PENDING,
            )
            .execution_options(skip_tenant_filter = True)
        ) or 0

    async def global_client_has_overlap(self, global_client_id: int, start: datetime, end: datetime) -> bool:
        """Active request of this client at any tenant overlapping [start, end) - pending, or
        confirmed with an appointment the tenant hasn't cancelled since."""
        stmt = (
            select(AppointmentRequest.id)
            .outerjoin(Appointment, and_(
                Appointment.id == AppointmentRequest.appointment_id,
                Appointment.tenant_id == AppointmentRequest.tenant_id,
            ))
            .where(
                AppointmentRequest.global_client_id == global_client_id,
                AppointmentRequest.start_time_est < end,
                AppointmentRequest.end_time_est > start,
                or_(
                    AppointmentRequest.status == AppointmentRequestStatus.PENDING,
                    and_(
                        AppointmentRequest.status == AppointmentRequestStatus.CONFIRMED,
                        Appointment.status != AppointmentStatus.CANCELLED,
                    ),
                ),
            )
            .limit(1)
            .execution_options(skip_tenant_filter = True)
        )
        result = await self.db.execute(stmt)
        return result.first() is not None

    # --- Background job: runs without tenant context (Celery session has no tenant filter) ---

    async def cancel_past_due(self, now: datetime) -> int:
        result = await self.db.execute(
            update(AppointmentRequest)
            .where(
                AppointmentRequest.status == AppointmentRequestStatus.PENDING,
                AppointmentRequest.expires_at <= now,
            )
            .values(
                status = AppointmentRequestStatus.CANCELLED,
                cancelled_reason = AppointmentRequestCancelledReason.PAST_DUE,
                decided_at = now,
            )
            .execution_options(synchronize_session = False)
        )
        return result.rowcount or 0
