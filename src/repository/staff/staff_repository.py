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

    async def get_or_create_actor(self, tenant_id: int, actor_type: str, name: str) -> Actor:
        """Non-staff actor (telegram/api/...) of a tenant - one per type, created on first use."""
        result = await self.db.execute(
            select(Actor)
            .where(Actor.tenant_id == tenant_id, Actor.actor_type == actor_type)
            .order_by(Actor.id)
            .limit(1)
        )
        actor = result.scalar_one_or_none()
        if actor is not None: return actor
        return await self.create_actor(Actor(tenant_id = tenant_id, actor_type = actor_type, name = name))

    async def get_active_with_roles(self) -> list[Staff]:
        result = await self.db.execute(
            select(Staff)
            .where(Staff.active.is_(True), Staff.archived.is_(False))
            .options(selectinload(Staff.roles))
        )
        return list(result.scalars().unique().all())

    async def get_id_by_actor(self, actor_id: int, tenant_id: int) -> int | None:
        return await self.db.scalar(
            select(Staff.id).where(Staff.actor_id == actor_id, Staff.tenant_id == tenant_id)
        )
