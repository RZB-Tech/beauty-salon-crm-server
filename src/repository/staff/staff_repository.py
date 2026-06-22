from sqlalchemy import select

from src.database.base import BaseRepository
from src.repository.staff.staff_model import Staff
from src.schemas.staff.create import StaffCreateDBSchema

class StaffRepository(BaseRepository):
    async def create(self, staff: StaffCreateDBSchema) -> Staff:
        self.db.add(staff)
        await self.db.commit()
        await self.db.refresh(staff)
        return staff

    async def get(self, login: str) -> Staff | None:
        result = await self.db.execute(
            select(Staff)
            .where(Staff.login == login)
        )
        return result.scalar_one_or_none()