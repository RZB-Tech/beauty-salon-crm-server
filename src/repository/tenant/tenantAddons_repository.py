from sqlalchemy import func, or_, select
from src.database.base import BaseRepository
from src.repository.tenant.subscription.subscriptionPlan_model import TenantAddon

class TenantAddonsRepository(BaseRepository[TenantAddon]):
    async def create(self, addon: TenantAddon) -> TenantAddon:
        self.db.add(addon)
        await self.db.flush()
        await self.db.refresh(addon)
        return addon

    async def get_by_tenant(self, tenant_id: int) -> list[TenantAddon]:
        result = await self.db.execute(
            select(TenantAddon)
            .where(TenantAddon.tenant_id == tenant_id)
            .order_by(TenantAddon.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_effective_limit(self, tenant_id: int, limit_key: str) -> int:
        """Extra capacity from this tenant's unexpired addons for `limit_key`."""
        # TenantAddon isn't TenantMixin, so nothing filters it by tenant automatically.
        result = await self.db.execute(
            select(func.coalesce(func.sum(TenantAddon.amount), 0)).where(
                TenantAddon.tenant_id == tenant_id,
                TenantAddon.limit_key == limit_key,
                or_(TenantAddon.expires_at.is_(None), TenantAddon.expires_at > func.now()),
            )
        )
        return result.scalar_one()
