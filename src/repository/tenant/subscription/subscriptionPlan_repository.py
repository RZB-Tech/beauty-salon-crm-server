from sqlalchemy import select
from src.database.base import BaseRepository
from src.repository.tenant.subscription.subscriptionPlan_model import SubscriptionPlan

class SubcriptionPlanRepository(BaseRepository[SubscriptionPlan]):
    async def create(self, plan: SubscriptionPlan) -> SubscriptionPlan:
        self.db.add(plan)
        await self.db.flush()
        await self.db.refresh(plan)
        return plan

    async def get(self, id: int) -> SubscriptionPlan | None:
        stmt = (
            select(SubscriptionPlan)
            .where(SubscriptionPlan.id == id)
            .execution_options(skip_tenant_filter = True)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> list[SubscriptionPlan]:
        stmt = (
            select(SubscriptionPlan)
            .where(SubscriptionPlan.is_visible.is_(True), SubscriptionPlan.archived.is_(False))
            .order_by(SubscriptionPlan.price.asc())
            .execution_options(skip_tenant_filter = True)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()