from sqlalchemy import Result, select

from src.database.base import BaseRepository
from src.repository.staff.staff_model import Staff

class StaffRepository(BaseRepository[Staff]):
    async def create(self, staff: Staff) -> Staff:
        self.db.add(staff)
        await self.db.flush()
        await self.db.refresh(staff)
        return staff

    async def get(self, id: int | None = None, login: str | None = None) -> Staff | None:
        result: Result | None
        if id:
            result = await self.db.execute(
                select(Staff)
                .where(Staff.id == id)
            )
        elif login:
            result = await self.db.execute(
                select(Staff)
                .where(Staff.login == login)
            )
        return result.scalar_one_or_none()