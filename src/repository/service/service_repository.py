from datetime import timedelta

from sqlalchemy import Row, and_, func, select
from sqlalchemy.orm import selectinload
from src.core.utils.model_filter import apply_dynamic_filters
from src.database.base import BaseRepository
from src.repository.appointment.appointment_model import Appointment, AppointmentRecords, AppointmentServices
from src.repository.service.service_model import Service
from src.schemas.analytics.request import GetReportWithFilters
from src.schemas.base import RequestAllObject
from src.schemas.service.create import ServiceCreateSchema

class ServiceRepository(BaseRepository[Service]):

    async def create(self, service: ServiceCreateSchema) -> Service:
        self.db.add(service)
        await self.db.flush()
        await self.db.refresh(service)
        return service
    
    async def get_with_employees(self, id: int) -> Service | None:
        stmt = (select(Service)
            .where(Service.id == id)
            .options(selectinload(Service.employees)))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_ids(self, ids: list[int]) -> list[Service]:
        result = await self.db.execute(
            select(Service).where(Service.id.in_(ids))
        )
        return result.scalars().all()
    
    async def get_all(self, data: RequestAllObject) -> tuple[list[Service], int]:
        count_stmt = select(func.count()).select_from(Service)
        stmt = select(Service)
        count_stmt = apply_dynamic_filters(count_stmt, Service, data.filters)
        stmt = apply_dynamic_filters(stmt, Service, data.filters)
        total_items = await self.db.scalar(count_stmt) or 0
        offset_value = (data.page - 1) * data.pageSize
        stmt = stmt.order_by(Service.id.desc()).offset(offset_value).limit(data.pageSize)
        result = await self.db.execute(stmt)
        items = result.scalars().all()
        return items, total_items

    async def get_analytics(self, data: GetReportWithFilters) -> list[Row]:
        stmt = (
            select(
                Service.name,
                AppointmentServices.service_id,
                func.count().label("amount"),
                func.sum(AppointmentServices.final_price).label("revenue"),
            )
            .select_from(Service)
            .where(Service.tenant_id == data.branch_id)
            .join(AppointmentServices,
                  and_(
                      AppointmentServices.service_id == Service.id,
                      AppointmentServices.tenant_id == data.branch_id
                  ))
            .join(AppointmentRecords,
                  and_(
                      AppointmentServices.appointment_record_id == AppointmentRecords.id,
                      AppointmentRecords.tenant_id == data.branch_id
                  ))
            .join(Appointment,
                  and_(
                      AppointmentRecords.appointment_id == Appointment.id,
                      Appointment.tenant_id == data.branch_id
                  ))
            .where(Appointment.paid.is_(True))
            .where(and_(
                AppointmentServices.service_id.isnot(None),
                AppointmentServices.created_at >= data.start_date,
                AppointmentServices.created_at < data.end_date + timedelta(days = 1)
            ))
            .group_by(Service.name, AppointmentServices.service_id)
            .execution_options(skip_tenant_filter = True)
        )

        result = await self.db.execute(stmt)
        return result.all()