from datetime import datetime

from sqlalchemy import func, select
from src.core.utils.model_filter import apply_dynamic_filters
from src.database.base import BaseRepository
from src.repository.appointment.appointment_model import AppointmentServices
from src.schemas.appointment.create import AppointmentServicesCreateSchema
from src.schemas.base import RequestAllObject

class AppointmentServicesRepository(BaseRepository):
    async def create(self, appointmentService: AppointmentServicesCreateSchema) -> AppointmentServices:
        self.db.add(appointmentService)
        await self.db.commit()
        await self.db.refresh(appointmentService)
        return appointmentService
    
    async def get_by_ids(self, ids: list[int]) -> list[AppointmentServices]:
        stmt = (
            select(AppointmentServices)
            .where(AppointmentServices.id.in_(ids))
        )
        return list(stmt.scalars().all())
    
    async def get(self, id: int) -> AppointmentServices | None:
        stmt = (
            select(AppointmentServices)
            .where(AppointmentServices.id == id)
        )

        result = await self.db.scalar(stmt)
        return result
    
    async def get_all(self, data: RequestAllObject) -> tuple[list[AppointmentServices], int]:
        count_stmt = select(func.count()).select_from(AppointmentServices)
        stmt = select(AppointmentServices)
        count_stmt = apply_dynamic_filters(count_stmt, AppointmentServices, data.filters)
        stmt = apply_dynamic_filters(stmt, AppointmentServices, data.filters)
        total_items = await self.db.scalar(count_stmt) or 0
        offset_value = (data.page - 1) * data.pageSize
        stmt = stmt.offset(offset_value).limit(data.pageSize)
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
    
    async def delete(self, id: int) -> bool:
        obj = await self.db.get(AppointmentServices, id)
        if not obj:
            return False

        await self.db.delete(obj)
        await self.db.commit()
        return True

    