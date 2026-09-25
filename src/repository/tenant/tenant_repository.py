from sqlalchemy import Result, select
from src.database.base import BaseRepository
from src.repository.tenant.tenant_model import Tenant

class TenantRepository(BaseRepository[Tenant]):
    async def get(self, id: int | None = None, name: str | None = None, lock: bool = False) -> Tenant | None:
        result: Result | None
        if id:
            stmt = select(Tenant).where(Tenant.id == id)
            # populate_existing: see BaseRepository.get - without it a tenant already
            # loaded earlier in the request keeps its stale balance under the lock.
            if lock: stmt = stmt.with_for_update().execution_options(populate_existing = True)
            result = await self.db.execute(stmt)
        elif name:
            result = await self.db.execute(
                select(Tenant)
                .where(Tenant.name == name)
            )
        return result.scalar_one_or_none()

    async def get_branches(self, parent_id: int) -> list[Tenant]:
        result = await self.db.execute(
            select(Tenant).where(Tenant.parent_id == parent_id)
        )
        return list(result.scalars().all())

    async def get_all_bookable(self) -> list[Tenant]:
        """Active tenants that enabled Telegram booking in their preferences."""
        result = await self.db.execute(
            select(Tenant)
            .where(
                Tenant.active.is_(True),
                Tenant.preferences["enable_telegram_booking"].as_boolean().is_(True),
            )
            .order_by(Tenant.name)
        )
        return list(result.scalars().all())
