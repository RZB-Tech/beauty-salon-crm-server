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
from src.schemas.tenantSubscription.response import (
    TenantBillingStateSchema,
    TenantSubscriptionInfoSchema,
    TenantSubscriptionResponseSchema,
)


class TenantSubscriptionService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get_current(self) -> TenantBillingStateSchema:
        tenantID = get_current_tenant_id()
        if tenantID is None: raise AuthTenantContextEmpty()

        tenant = await self.uow.tenants.get(id = tenantID)
        if tenant is None: raise TenantNotFound(tenantID)

        subscription = await self.uow.tenantSubscriptions.get_by_tenant(tenantID)
        has_active = (
            subscription is not None
            and subscription.status in (TenantSubscriptionStatus.ACTIVE, TenantSubscriptionStatus.TRIAL)
            and subscription.period_end > datetime.now(timezone.utc)
        )

        return TenantBillingStateSchema(
            balance = tenant.balance,
            has_active_subscription = has_active,
            subscription = TenantSubscriptionInfoSchema.model_validate(subscription) if subscription else None,
        )

    async def purchase(self, data: TenantSubscriptionPurchaseSchema) -> TenantSubscriptionResponseSchema:
        tenantID = get_current_tenant_id()
        if tenantID is None: raise AuthTenantContextEmpty()

        result = await self.purchase_for_tenant(tenantID, data.plan_id)

        # Commit, THEN clear the cache. FastAPI's own commit runs only after the
        # response is sent, so clearing first would let the client's very next
        # request read the old uncommitted state and re-cache "inactive" for
        # the full cache TTL.
        await self.uow.db.commit()
        await delete_tenant_active(tenantID)

        return result

    async def purchase_for_tenant(self, tenant_id: int, plan_id: int) -> TenantSubscriptionResponseSchema:
        """
        The spend-balance-and-activate logic, taking the tenant explicitly so it
        is callable from both `purchase()` and the Celery auto-pay task.
        Does not commit or clear the tenant-active cache: callers must do both,
        in that order, once their transaction is done.
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
