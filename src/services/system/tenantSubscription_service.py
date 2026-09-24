from datetime import datetime, timedelta, timezone

from src.core.cache.tenant_cache import delete_tenant_active
from src.core.dependencies.context import get_current_tenant_id
from src.core.dependencies.uow import UnitOfWork
from src.exceptions.auth_exceptions import AuthTenantContextEmpty
from src.exceptions.general_exceptions import ObjectIsArchived
from src.exceptions.subscriptionPlan_exceptions import SubscriptionPlanNotFound
from src.exceptions.tenant_exceptions import TenantInsufficientBalance, TenantNotFound
from src.repository.tenant.payments.tenantExpeses_model import TenantExpenseCategory, TenantExpenses
from src.repository.tenant.tenant_model import TenantSubscriptions, TenantSubscriptionStatus
from src.schemas.tenantSubscription.purchase import TenantSubscriptionPurchaseSchema
from src.schemas.tenantSubscription.response import TenantSubscriptionResponseSchema


class TenantSubscriptionService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def purchase(self, data: TenantSubscriptionPurchaseSchema) -> TenantSubscriptionResponseSchema:
        tenantID = get_current_tenant_id()
        if tenantID is None: raise AuthTenantContextEmpty()

        return await self.purchase_for_tenant(tenantID, data.plan_id)

    async def purchase_for_tenant(self, tenant_id: int, plan_id: int) -> TenantSubscriptionResponseSchema:
        """
        The actual spend-balance-and-activate logic, taking the tenant explicitly
        rather than from request context - so it's callable both from the
        authenticated `purchase()` above and from the Celery auto-pay task,
        which has no request/staff context to read a tenant from.
        """
        plan = await self.uow.subscriptionsPlans.get(plan_id)
        if plan is None: raise SubscriptionPlanNotFound(plan_id)
        if plan.archived: raise ObjectIsArchived(plan_id, "subscription_plans")

        # Lock the tenant row for the whole spend-and-activate sequence: the
        # balance check and the deduction must happen against the same,
        # unchanging value, or two concurrent purchases could both pass the
        # check against a stale balance and overspend it.
        tenant = await self.uow.tenants.get(id = tenant_id, lock = True)
        if tenant is None: raise TenantNotFound(tenant_id)

        if tenant.balance < plan.price:
            raise TenantInsufficientBalance(tenant_id, plan.price, tenant.balance)

        tenant.balance = tenant.balance - plan.price

        await self.uow.tenantExpenses.create(TenantExpenses(
            tenant_id = tenant.id,
            tenant_snapshot = {"id": tenant.id, "name": tenant.name, "TIN": tenant.TIN},
            amount = plan.price,
            category = TenantExpenseCategory.SUBSCRIPTION,
            description = f"Subscription plan: {plan.name}",
            expense_metadata = {"plan_id": plan.id},
        ))

        now = datetime.now(timezone.utc)
        period_end = now + timedelta(days = plan.duration_days)

        # Buying always resets the period to now + duration, even if the
        # tenant still has time left on a current subscription - renewing
        # early does not carry the remainder over.
        subscription = await self.uow.tenantSubscriptions.get_by_tenant(tenant_id, lock = True)
        if subscription is None:
            subscription = await self.uow.tenantSubscriptions.create(TenantSubscriptions(
                tenant_id = tenant.id,
                plan_id = plan.id,
                status = TenantSubscriptionStatus.ACTIVE,
                amount_paid = plan.price,
                started_at = now,
                period_end = period_end,
            ))
        else:
            subscription.plan_id = plan.id
            subscription.status = TenantSubscriptionStatus.ACTIVE
            subscription.amount_paid = plan.price
            subscription.started_at = now
            subscription.period_end = period_end

        # Bust the cached subscription-active flag immediately - otherwise the
        # tenant stays locked out of the rest of the app for up to the cache's
        # TTL (REFRESH_TOKEN_EXPIRE_SECONDS) right after having just paid.
        await delete_tenant_active(tenant.id)

        return TenantSubscriptionResponseSchema(
            id = subscription.id,
            tenant_id = subscription.tenant_id,
            plan_id = subscription.plan_id,
            status = subscription.status,
            amount_paid = subscription.amount_paid,
            started_at = subscription.started_at,
            period_end = subscription.period_end,
            tenant_balance = tenant.balance,
        )
