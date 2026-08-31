from sqlalchemy import Result, func, select
from sqlalchemy.orm import selectinload

from src.core.utils.model_filter import apply_dynamic_filters
from src.database.base import Actor, BaseRepository
from src.repository.staff.staff_model import Staff
from src.schemas.base import RequestAllObject

class StaffRepository(BaseRepository[Staff]):
    async def create(self, staff: Staff) -> Staff:
        self.db.add(staff)
        await self.db.flush()
        await self.db.refresh(staff)
        return staff 

    async def create_actor(self, actor: Actor) -> Actor:
        self.db.add(actor)
        await self.db.flush()
        await self.db.refresh(actor)
        return actor

    async def get(self, id: int | None = None, login: str | None = None) -> Staff | None:
        result: Result | None
        if id is not None:
            result = await self.db.execute(
                select(Staff)
                .where(Staff.id == id)
                .options(selectinload(Staff.roles))
            )
        elif login is not None:
            result = await self.db.execute(
                select(Staff)
                .where(Staff.login == login)
                .options(selectinload(Staff.roles))
            )
        return result.scalar_one_or_none()

    async def get_all(self, data: RequestAllObject) -> tuple[list[Staff], int]:
        count_stmt = select(func.count()).select_from(Staff)
        stmt = select(Staff)
        count_stmt = apply_dynamic_filters(count_stmt, Staff, data.filters)
        stmt = apply_dynamic_filters(stmt, Staff, data.filters)
        total_items = await self.db.scalar(count_stmt) or 0
        offset_value = (data.page - 1) * data.pageSize
        stmt = (
            stmt.options(selectinload(Staff.roles))
            .order_by(Staff.id.asc())
            .offset(offset_value)
            .limit(data.pageSize)
        )
        result = await self.db.execute(stmt)
        items = result.scalars().all()
        return items, total_items