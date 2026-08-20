from sqlalchemy import Result, select
from src.database.base import BaseRepository
from src.repository.tenant.tenant_model import Tenant

class TenantRepository(BaseRepository[Tenant]):
    async def get(self, id: int | None = None, name: str | None = None) -> Tenant | None:
        result: Result | None
        if id:
            result = await self.db.execute(
                select(Tenant)
                .where(Tenant.id == id)
            )
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