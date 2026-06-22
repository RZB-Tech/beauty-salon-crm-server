from sqlalchemy import func, select

from src.database.base import BaseRepository
from src.repository.employee.workSchedule_model import EmployeeAbsence
from src.schemas.base import RequestAllObject
from src.schemas.work_schedule.update import AbsenceUpdateSchema

class EmployeeAbsenceRepository(BaseRepository):
    async def create(self, absence: EmployeeAbsence) -> EmployeeAbsence:
        self.db.add(absence)
        await self.db.commit()
        await self.db.refresh(absence)
        return absence

    async def get(self, id: int) -> EmployeeAbsence | None:
        return await self.db.get(EmployeeAbsence, id)
    
    async def get_all(self, data: RequestAllObject) -> tuple[list[EmployeeAbsence], int]:
        count_stmt = select(func.count()).select_from(EmployeeAbsence)
        total_items = await self.db.scalar(count_stmt) or 0
        offset_value = (data.page - 1) * data.pageSize
        stmt = (
            select(EmployeeAbsence)
            .offset(offset_value)
            .limit(data.pageSize)
        )
        result = await self.db.execute(stmt)
        items = list(result.scalars().all())
        return items, total_items

    async def get_by_ids(self, ids: list[int]) -> list[EmployeeAbsence]:
        result = await self.db.execute(
            select(EmployeeAbsence)
            .where(EmployeeAbsence.id.in_(ids))
        )
        return list(result.scalars().all())
    
    async def update(self, data: AbsenceUpdateSchema) -> EmployeeAbsence | None:
        obj = await self.db.get(EmployeeAbsence, data.id)
        if not obj:
            return None

        update_data = data.model_dump(exclude_unset=True)
        update_data.pop("id", None)

        for field, value in update_data.items():
            setattr(obj, field, value) 

        await self.db.commit()
        await self.db.refresh(obj)

        return obj
    
    async def delete(self, id: int) -> bool:
        obj = await self.db.get(EmployeeAbsence, id)
        if not obj:
            return False

        await self.db.delete(obj)
        await self.db.commit()
        return True