from sqlalchemy import func, or_, select
from src.database.base import BaseRepository
from src.repository.tenant.subscription.subscriptionPlan_model import TenantAddon

class TenantAddonsRepository(BaseRepository[TenantAddon]):
    async def create(self, addon: TenantAddon) -> TenantAddon:
        self.db.add(addon)
        await self.db.flush()
        await self.db.refresh(addon)
        return addon

    async def get_effective_limit(self, limit_key: str) -> int:
        result = await self.db.execute(
            select(func.coalesce(func.sum(TenantAddon.amount), 0)).where(
                TenantAddon.limit_key == limit_key,
                or_(TenantAddon.expires_at.is_(None), TenantAddon.expires_at > func.now()),
            )
        )
        return result.scalar_one()
