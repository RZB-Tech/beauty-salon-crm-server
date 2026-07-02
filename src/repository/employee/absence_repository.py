from sqlalchemy import func, select

from src.database.base import BaseRepository
from src.repository.employee.workSchedule_model import EmployeeAbsence
from src.schemas.base import RequestAllObject
from src.schemas.work_schedule.update import AbsenceUpdateSchema

class EmployeeAbsenceRepository(BaseRepository[EmployeeAbsence]):
    async def create(self, absence: EmployeeAbsence) -> EmployeeAbsence:
        self.db.add(absence)
        await self.db.flush()
        await self.db.refresh(absence)
        return absence
    
    async def get_all(self, data: RequestAllObject) -> tuple[list[EmployeeAbsence], int]:
        count_stmt = select(func.count()).select_from(EmployeeAbsence)
        total_items = await self.db.scalar(count_stmt) or 0
        offset_value = (data.page - 1) * data.pageSize
        stmt = (
            select(EmployeeAbsence)
            .order_by(EmployeeAbsence.id.desc())
            .offset(offset_value)
            .limit(data.pageSize)
        )
        result = await self.db.execute(stmt)
        items = result.scalars().all()
        return items, total_items

    async def get_by_ids(self, ids: list[int]) -> list[EmployeeAbsence]:
        result = await self.db.execute(
            select(EmployeeAbsence)
            .where(EmployeeAbsence.id.in_(ids))
        )
        return result.scalars().all()