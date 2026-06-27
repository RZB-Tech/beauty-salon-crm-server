from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from src.core.utils.model_filter import apply_dynamic_filters
from src.database.base import BaseRepository
from src.repository.appointment.appointment_model import Appointment, AppointmentRecords, AppointmentServices, AppointmentStatus
from src.schemas.appointment.create import AppointmentRecordsCreateSchema
from src.schemas.base import RequestAllObject

class AppointmentRecordsRepository(BaseRepository):
    async def create(self, appointmentRecord: AppointmentRecordsCreateSchema) -> AppointmentRecords:
        db_services = [
            AppointmentServices(
                service_id = service.service_id,
                material_id = service.material_id,
                quantity = service.quantity,
                price = service.price,
                price_changed_reason = service.price_changed_reason,
                notes = service.notes
            )
            for service in appointmentRecord.services
        ]

        db_appointmentRecord = AppointmentRecords(
            appointment_id = appointmentRecord.appointment_id,
            employee_id = appointmentRecord.employee_id,
            services = db_services
        )

        self.db.add(db_appointmentRecord)
        await self.db.commit()
        await self.db.refresh(db_appointmentRecord)
        return db_appointmentRecord
    
    async def get_by_ids(self, ids: list[int]) -> list[AppointmentRecords]:
        stmt = (
            select(AppointmentRecords)
            .where(AppointmentRecords.id.in_(ids))
            .options(selectinload(AppointmentRecords.services))
        )
        return list(stmt.scalars().all())
    
    async def get(self, id: int) -> AppointmentRecords | None:
        stmt = (
            select(AppointmentRecords)
            .where(AppointmentRecords.id == id)
            .options(selectinload(AppointmentRecords.services))
        )

        result = await self.db.scalar(stmt)
        return result
    
    async def get_all(self, data: RequestAllObject) -> tuple[list[AppointmentRecords], int]:
        count_stmt = select(func.count()).select_from(AppointmentRecords)
        stmt = select(AppointmentRecords)
        count_stmt = apply_dynamic_filters(count_stmt, AppointmentRecords, data.filters)
        stmt = apply_dynamic_filters(stmt, AppointmentRecords, data.filters)
        total_items = await self.db.scalar(count_stmt) or 0
        offset_value = (data.page - 1) * data.pageSize
        stmt = stmt.options(selectinload(AppointmentRecords.services)).offset(offset_value).limit(data.pageSize)
        result = await self.db.execute(stmt)
        items = list(result.scalars().all())
        return items, total_items
    
    # async def update(self, payload: MaterialUpdateSchema) -> Material | None:
    #     obj = await self.db.get(Material, payload.id)
    #     if not obj:
    #         return None

    #     update_data = payload.model_dump(exclude_unset=True)

    #     update_data.pop("id", None)

    #     for field, value in update_data.items():
    #         setattr(obj, field, value)

    #     await self.db.commit()
    #     await self.db.refresh(obj)

    #     return obj

    async def employee_has_overlap(self, employeeID: int, start: datetime, end: datetime) -> bool:
        stmt = (
            select(func.count(AppointmentRecords.id))
            .join(Appointment, AppointmentRecords.appointment_id == Appointment.id)
            .where(
                AppointmentRecords.employee_id == employeeID,
                Appointment.status != AppointmentStatus.CANCELLED,
                Appointment.start_time_est < end,
                Appointment.end_time_est > start
            )
        )

        count = await self.db.scalar(stmt)
        return count > 0