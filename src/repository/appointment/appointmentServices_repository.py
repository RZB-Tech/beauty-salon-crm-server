from sqlalchemy import Result, func, select
from sqlalchemy.orm import selectinload
from src.core.utils.model_filter import apply_dynamic_filters
from src.database.base import BaseRepository
from src.repository.appointment.appointment_model import AppointmentServices
from src.schemas.appointment.create import AppointmentServicesCreateSchema
from src.schemas.base import RequestAllObject

class AppointmentServicesRepository(BaseRepository[AppointmentServices]):
    async def create(self, appointmentService: AppointmentServicesCreateSchema) -> AppointmentServices:
        self.db.add(appointmentService)
        await self.db.flush()
        await self.db.refresh(appointmentService)
        return appointmentService
    
    async def get(self, id: int) -> AppointmentServices:
        result: Result = await self.db.execute(
            select(AppointmentServices)
            .where(AppointmentServices.id == id)
            .options(selectinload(AppointmentServices.appointment_record))
        )
        return result.scalar_one_or_none()
    
    async def get_by_ids(self, ids: list[int]) -> list[AppointmentServices]:
        stmt = (
            select(AppointmentServices)
            .where(AppointmentServices.id.in_(ids))
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_all(self, data: RequestAllObject) -> tuple[list[AppointmentServices], int]:
        count_stmt = select(func.count()).select_from(AppointmentServices)
        stmt = select(AppointmentServices)
        count_stmt = apply_dynamic_filters(count_stmt, AppointmentServices, data.filters)
        stmt = apply_dynamic_filters(stmt, AppointmentServices, data.filters)
        total_items = await self.db.scalar(count_stmt) or 0
        offset_value = (data.page - 1) * data.pageSize
        stmt = stmt.offset(offset_value).limit(data.pageSize)
        result = await self.db.execute(stmt)
        items = result.scalars().all()
        return items, total_items