from sqlalchemy import select

from src.database.base import BaseRepository
from src.repository.system.tenant_model import TenantPreferences


class TenantPreferencesRepository(BaseRepository[TenantPreferences]):
    async def create(self, preferences: TenantPreferences) -> TenantPreferences:
        self.db.add(preferences)
        await self.db.flush()
        await self.db.refresh(preferences)
        return preferences

    async def get_by_tenant_id(self, tenant_id: int) -> TenantPreferences | None:
        result = await self.db.execute(
            select(TenantPreferences).where(TenantPreferences.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()

    async def update_by_tenant_id(
        self,
        tenant_id: int,
        preferences: dict,
    ) -> TenantPreferences | None:
        obj = await self.get_by_tenant_id(tenant_id)
        if obj is None:
            return None

        obj.preferences = preferences
        await self.db.flush()
        await self.db.refresh(obj)
        return obj
