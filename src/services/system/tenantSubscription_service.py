from datetime import datetime, timedelta, timezone

from src.core.cache.tenant_cache import delete_tenant_active
from src.core.dependencies.context import get_current_tenant_id
from src.core.dependencies.uow import UnitOfWork
from src.exceptions.auth_exceptions import AuthTenantContextEmpty
from src.exceptions.general_exceptions import ObjectIsArchived
from src.exceptions.subscriptionPlan_exceptions import AddonProductNotFound, SubscriptionPlanNotFound
from src.exceptions.tenant_exceptions import (
    TenantInsufficientBalance,
    TenantNotFound,
    TenantSubscriptionAlreadyActive,
)
from src.repository.tenant.payments.tenantExpeses_model import TenantExpenseCategory, TenantExpenses
from src.repository.tenant.subscription.subscriptionPlan_model import TenantAddon
from src.repository.tenant.tenant_model import TenantSubscriptions, TenantSubscriptionStatus
from src.schemas.tenantSubscription.addon import (
    AddonProductResponseSchema,
    AddonPurchaseResponseSchema,
    AddonPurchaseSchema,
    TenantAddonResponseSchema,
)
from src.schemas.tenantSubscription.purchase import TenantSubscriptionPurchaseSchema
from src.schemas.tenantSubscription.response import (
    TenantBillingStateSchema,
    TenantLimitsSchema,
    TenantLimitUsageSchema,
    TenantSubscriptionInfoSchema,
    TenantSubscriptionResponseSchema,
)
from src.services.system.tenantLimits_service import get_limits_usage


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

    async def get_limits(self) -> TenantLimitsSchema:
        tenantID = get_current_tenant_id()
        if tenantID is None: raise AuthTenantContextEmpty()

        plan_id, usages = await get_limits_usage(self.uow, tenantID)
        return TenantLimitsSchema(
            plan_id = plan_id,
            limits = [
                TenantLimitUsageSchema(
                    limit_key = u.limit.value,
                    plan = u.plan,
                    addons = u.addons,
                    allowed = u.allowed,
                    used = u.used,
                    remaining = None if u.allowed is None else max(0, u.allowed - u.used),
                )
                for u in usages
            ],
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
        Raises every domain error before changing anything.
        """
        # Hidden plans (is_visible = False) are deliberately purchasable: they're
        # only kept out of the public plan listing, not blocked here.
        plan = await self.uow.subscriptionsPlans.get(plan_id)
        if plan is None: raise SubscriptionPlanNotFound(plan_id)
        if plan.archived: raise ObjectIsArchived(plan_id, "subscription_plans")

        # Lock the tenant row for the whole spend-and-activate sequence: the
        # balance check and the deduction must happen against the same,
        # unchanging value, or two concurrent purchases could both pass the
        # check against a stale balance and overspend it.
        tenant = await self.uow.tenants.get(id = tenant_id, lock = True)
        if tenant is None: raise TenantNotFound(tenant_id)

        # Lock the subscription too (tenant first, then subscription - the order
        # used everywhere), so the check below can't race another purchase.
        subscription = await self.uow.tenantSubscriptions.get_by_tenant(tenant_id, lock = True)
        now = datetime.now(timezone.utc)

        # Buying a plan the tenant is already paying for would reset its period
        # and charge again - this is what stops a double click from charging twice.
        # A trial of the same plan can still be converted to a paid subscription.
        if (
            subscription is not None
            and subscription.status == TenantSubscriptionStatus.ACTIVE
            and subscription.plan_id == plan.id
            and subscription.period_end > now
        ):
            raise TenantSubscriptionAlreadyActive(tenant_id, plan.id)

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

        period_end = now + timedelta(days = plan.duration_days)

        # Buying always resets the period to now + duration, even if the
        # tenant still has time left on a current subscription (e.g. switching
        # plans) - the remainder is not carried over.
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

    async def get_addon_products(self) -> list[AddonProductResponseSchema]:
        products = await self.uow.addonProducts.get_all_available()
        return [AddonProductResponseSchema.model_validate(p) for p in products]

    async def get_addons(self) -> list[TenantAddonResponseSchema]:
        tenantID = get_current_tenant_id()
        if tenantID is None: raise AuthTenantContextEmpty()

        addons = await self.uow.tenantAddons.get_by_tenant(tenantID)
        return [TenantAddonResponseSchema.model_validate(a) for a in addons]

    async def purchase_addon(self, data: AddonPurchaseSchema) -> AddonPurchaseResponseSchema:
        """
        Spends the product's price from the balance, records the expense and
        grants the addon - all in one transaction. The addon belongs to the
        buying tenant only; a parent's addons don't reach its branches.
        Buying the same product again is allowed: addons stack.
        """
        tenantID = get_current_tenant_id()
        if tenantID is None: raise AuthTenantContextEmpty()

        product = await self.uow.addonProducts.get(data.product_id)
        if product is None or product.archived: raise AddonProductNotFound(data.product_id)

        # Same reason as purchase_for_tenant: check and deduct against a locked balance.
        tenant = await self.uow.tenants.get(id = tenantID, lock = True)
        if tenant is None: raise TenantNotFound(tenantID)

        if tenant.balance < product.price:
            raise TenantInsufficientBalance(tenantID, product.price, tenant.balance)

        tenant.balance = tenant.balance - product.price

        expense = await self.uow.tenantExpenses.create(TenantExpenses(
            tenant_id = tenant.id,
            tenant_snapshot = {"id": tenant.id, "name": tenant.name, "TIN": tenant.TIN},
            amount = product.price,
            category = TenantExpenseCategory.FEATURE_PURCHASE,
            description = f"Addon: {product.name}",
            expense_metadata = {
                "addon_product_id": product.id,
                "limit_key": product.limit_key,
                "amount": product.amount,
            },
        ))

        # limit_key/amount are copied, not read through product_id, so a later
        # edit of the product never changes what was bought here. Never expires.
        addon = await self.uow.tenantAddons.create(TenantAddon(
            tenant_id = tenant.id,
            limit_key = product.limit_key,
            amount = product.amount,
            product_id = product.id,
            expense_id = expense.id,
            expires_at = None,
        ))

        # Commit before answering, like purchase(): FastAPI's own commit runs
        # only after the response is sent.
        await self.uow.db.commit()

        return AddonPurchaseResponseSchema(
            addon = TenantAddonResponseSchema.model_validate(addon),
            tenant_balance = tenant.balance,
        )
