import asyncio
import logging

from src.core.cache.tenant_cache import delete_tenant_active
from src.core.celery.celeryApp import celery_app
from src.core.celery.session import celery_transaction_scope
from src.core.dependencies.uow import UnitOfWork
from src.exceptions.tenant_exceptions import TenantInsufficientBalance
from src.repository.tenant.tenant_model import TenantSubscriptionStatus
from src.schemas.tenant.base import TenantPreferencesSchema
from src.services.system.tenantSubscription_service import TenantSubscriptionService

logger = logging.getLogger(__name__)

_EXPIRABLE_STATUSES = (TenantSubscriptionStatus.ACTIVE, TenantSubscriptionStatus.TRIAL)

@celery_app.task(name="expire_tenant_subscriptions")
def expire_tenant_subscriptions():
    asyncio.run(_expire_tenant_subscriptions())

async def _expire_tenant_subscriptions():
    # Read-only pass to find candidates - kept separate from the per-tenant
    # writes below so we're not holding a lock on every candidate's row for
    # the duration of the whole batch.
    async with celery_transaction_scope():
        uow = UnitOfWork()
        expired = await uow.tenantSubscriptions.get_expired(_EXPIRABLE_STATUSES)
        candidates = [(s.tenant_id, s.plan_id) for s in expired]

    renewed_ids: list[int] = []
    past_due_ids: list[int] = []
    failed_ids: list[int] = []

    # One transaction per tenant: keeps each row's lock short-lived, and one
    # tenant's failure can't roll back what already succeeded for another.
    for tenant_id, plan_id in candidates:
        try:
            async with celery_transaction_scope():
                uow = UnitOfWork()
                tenant = await uow.tenants.get(id = tenant_id)
                if tenant is None:
                    continue

                preferences = TenantPreferencesSchema(**tenant.preferences)
                renewed = False

                if preferences.auto_pay_subscription:
                    try:
                        # Renews the SAME plan the tenant was already on - this
                        # reuses the exact lock/balance-check/expense/activate
                        # sequence the manual purchase endpoint uses, so auto-pay
                        # can't drift from what a human clicking "pay" would get.
                        await TenantSubscriptionService(uow).purchase_for_tenant(tenant_id, plan_id)
                        renewed = True
                    except TenantInsufficientBalance:
                        logger.warning(
                            f"Tenant {tenant_id} has auto_pay_subscription enabled but insufficient "
                            f"balance to renew plan {plan_id}; marking past due instead."
                        )

                if not renewed:
                    subscription = await uow.tenantSubscriptions.get_by_tenant(tenant_id, lock = True)
                    if subscription is not None:
                        subscription.status = TenantSubscriptionStatus.PAST_DUE

            await delete_tenant_active(tenant_id)
            (renewed_ids if renewed else past_due_ids).append(tenant_id)
        except Exception:
            logger.exception(f"Failed to process expiring subscription for tenant {tenant_id}")
            failed_ids.append(tenant_id)

    logger.info(
        f"Subscription expiry pass done: renewed={renewed_ids} past_due={past_due_ids} failed={failed_ids}"
    )
