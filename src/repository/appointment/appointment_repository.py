from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from src.core.utils.model_filter import apply_dynamic_filters
from src.database.base import BaseRepository
from src.repository.appointment.appointment_model import Appointment, AppointmentRecords, AppointmentServices, AppointmentStatus
from src.schemas.base import PaginationSchema, RequestAllObject
from src.schemas.appointment.create import AppointmentCreateSchema

class AppointmentRepository(BaseRepository):
    async def create(self, appointment: AppointmentCreateSchema) -> Appointment:
        db_appointment = Appointment(
            client_id=appointment.client_id,
            start_time_est=appointment.start_time_est,
            end_time_est=appointment.end_time_est,
            notes=appointment.notes,
            records=[
                AppointmentRecords(
                    employee_id=record_data.employee_id,
                    services=[
                        AppointmentServices(
                            service_id=srv.service_id,
                            material_id = srv.material_id,
                            quantity = srv.quantity,
                            price = srv.price,
                            price_changed_reason = srv.price_changed_reason,
                            notes = srv.notes                    
                        )
                        for srv in record_data.services
                    ]
                )
                for record_data in (appointment.records or [])
            ]
        )

        self.db.add(db_appointment)
        await self.db.flush()
        await self.db.refresh(db_appointment)

        stmt = (
            select(Appointment)
            .where(Appointment.id == db_appointment.id)
            .options(selectinload(Appointment.records)
                     .selectinload(AppointmentRecords.services))
        )

        return await self.db.scalar(stmt)
    
    async def get_by_ids(self, ids: list[int]) -> list[Appointment]:
        stmt = (
            select(Appointment)
            .where(Appointment.id.in_(ids))
            .options(selectinload(Appointment.records)
                     .selectinload(AppointmentRecords.services))
        )
        return list(stmt.scalars().all())
    
    async def get(self, id: int) -> Appointment | None:
        stmt = (
            select(Appointment)
            .where(Appointment.id == id)
            .options(selectinload(Appointment.records)
                     .selectinload(AppointmentRecords.services))
        )

        result = await self.db.scalar(stmt)
        return result
    
    async def get_all(self, data: RequestAllObject) -> tuple[list[Appointment], int]:
        count_stmt = select(func.count()).select_from(Appointment)
        stmt = select(Appointment)
        count_stmt = apply_dynamic_filters(count_stmt, Appointment, data.filters)
        stmt = apply_dynamic_filters(stmt, Appointment, data.filters)
        total_items = await self.db.scalar(count_stmt) or 0
        offset_value = (data.page - 1) * data.pageSize
        stmt = (stmt
                .options(selectinload(Appointment.records)
                     .selectinload(AppointmentRecords.services))
                .order_by(Appointment.id.desc())
                .offset(offset_value)
                .limit(data.pageSize))
        result = await self.db.execute(stmt)
        items = list(result.scalars().all())
        return items, total_items

    async def cancel(self, appointment: Appointment) -> Appointment:
        appointment.status = AppointmentStatus.CANCELLED
        await self.db.flush()
        await self.db.refresh(appointment)
        return appointment

    async def client_has_overlap(self, clientID: int, start: datetime, end: datetime) -> bool:
        return await self.db.scalar(
            select(Appointment).where(
                Appointment.client_id == clientID,
                Appointment.start_time_est == start,
                Appointment.end_time_est == end
            )
        )
    
    async def get_by_client(self, data: PaginationSchema, id: int) -> tuple[list[Appointment], int]:
        count_stmt = (select(func.count())
            .select_from(Appointment)
            .where(Appointment.client_id == id)
            )
        total_items = await self.db.scalar(count_stmt) or 0
        offset_value = (data.page - 1) * data.pageSize
        stmt = (
            select(Appointment)
            .where(Appointment.client_id == id)
            .order_by(Appointment.id.desc())
            .options(selectinload(Appointment.records)
                     .selectinload(AppointmentRecords.services))
            .offset(offset_value)
            .limit(data.pageSize)
        )
        result = await self.db.execute(stmt)
        items = list(result.scalars().all())
        return items, total_items
    
    async def get_by_employee(self, data: PaginationSchema, id: int) -> tuple[list[Appointment], int]:
        baseStmt = (
            select(Appointment)
            .join(Appointment.records)
            .where(AppointmentRecords.employee_id == id)
        )

        countStmt = (
            select(func.count(Appointment.id))
            .join(Appointment.records)
            .where(AppointmentRecords.employee_id == id)
        )
        total_items = await self.db.scalar(countStmt) or 0

        offset_value = (data.page - 1) * data.pageSize
        stmt = (
            baseStmt
            .order_by(Appointment.id.desc())
            .options(
                selectinload(Appointment.records)
                .selectinload(AppointmentRecords.services)
            )
            .offset(offset_value)
            .limit(data.pageSize)
        )

        result = await self.db.execute(stmt)
        items = list(result.scalars().unique().all())
        return items, total_items