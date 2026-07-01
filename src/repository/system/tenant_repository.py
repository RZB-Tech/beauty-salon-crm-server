from sqlalchemy import Result, select
from src.database.base import BaseRepository
from src.repository.system.tenant_model import Tenant

class TenantRepository(BaseRepository[Tenant]):
    async def create(self, staff: Tenant) -> Tenant:
        self.db.add(staff)
        await self.db.flush()
        await self.db.refresh(staff)
        return staff

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