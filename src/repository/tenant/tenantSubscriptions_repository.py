from typing import Sequence

from sqlalchemy import func, select
from src.database.base import BaseRepository
from src.repository.tenant.tenant_model import TenantSubscriptions

class TenantSubscriptionsRepository(BaseRepository[TenantSubscriptions]):
    async def create(self, subscription: TenantSubscriptions) -> TenantSubscriptions:
        self.db.add(subscription)
        await self.db.flush()
        await self.db.refresh(subscription)
        return subscription

    async def get_by_tenant(self, tenant_id: int, lock: bool = False) -> TenantSubscriptions | None:
        stmt = select(TenantSubscriptions).where(TenantSubscriptions.tenant_id == tenant_id)
        if lock: stmt = stmt.with_for_update().execution_options(populate_existing = True)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_expired(self, statuses: Sequence[str]) -> list[TenantSubscriptions]:
        """Rows still labeled as one of `statuses` whose `period_end` has already passed."""
        stmt = select(TenantSubscriptions).where(
            TenantSubscriptions.status.in_(statuses),
            TenantSubscriptions.period_end <= func.now(),
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
