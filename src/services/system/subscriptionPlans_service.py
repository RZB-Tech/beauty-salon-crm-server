from src.core.dependencies.uow import UnitOfWork
from src.repository.tenant.subscription.subscriptionPlan_model import SubscriptionPlan
from src.exceptions.subscriptionPlan_exceptions import SubscriptionPlanNotFound

class SubscriptionPlanService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get(self, id: int) -> SubscriptionPlan:
        plan = await self.uow.subscriptionsPlans.get(id)
        # Hidden and archived plans are never listed publicly, same as get_all -
        # answer "not found" so they can't be discovered by id either.
        if plan is None or not plan.is_visible or plan.archived: raise SubscriptionPlanNotFound(id)
        return plan

    async def get_all(self) -> list[SubscriptionPlan]:
        return await self.uow.subscriptionsPlans.get_all()