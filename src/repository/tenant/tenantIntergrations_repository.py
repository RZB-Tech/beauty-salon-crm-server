from sqlalchemy import select
from src.database.base import BaseRepository
from src.repository.tenant.tenant_model import TenantIntegration

class TenantIntegrationsRepository(BaseRepository[TenantIntegration]):
    async def create(self, preferences: TenantIntegration) -> TenantIntegration:
        self.db.add(preferences)
        await self.db.flush()
        await self.db.refresh(preferences)
        return preferences

    async def get_by_tenant_id(self, tenant_id: int) -> TenantIntegration | None:
        result = await self.db.execute(
            select(TenantIntegration).where(TenantIntegration.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()