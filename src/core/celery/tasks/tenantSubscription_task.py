import asyncio
import logging
from datetime import datetime, timezone

from src.core.cache.tenant_cache import delete_tenant_active
from src.core.celery.celeryApp import celery_app
from src.core.celery.session import celery_transaction_scope
from src.core.dependencies.uow import UnitOfWork
from src.exceptions.base import BaseAppException
from src.repository.tenant.tenant_model import TenantSubscriptionStatus
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
        candidate_tenant_ids = [s.tenant_id for s in expired]

    renewed_ids: list[int] = []
    past_due_ids: list[int] = []
    skipped_ids: list[int] = []
    failed_ids: list[int] = []

    # One transaction per tenant: keeps each row's lock short-lived, and one
    # tenant's failure can't roll back what already succeeded for another.
    for tenant_id in candidate_tenant_ids:
        try:
            async with celery_transaction_scope():
                uow = UnitOfWork()
                # Lock tenant, then subscription - the same order
                # purchase_for_tenant uses, so the two can't deadlock.
                tenant = await uow.tenants.get(id = tenant_id, lock = True)
                subscription = await uow.tenantSubscriptions.get_by_tenant(tenant_id, lock = True)

                # The candidate list is a snapshot; the tenant may have renewed
                # manually since. Re-check under lock, or we'd charge them twice
                # or mark a freshly paid subscription past due.
                if (
                    tenant is None
                    or subscription is None
                    or subscription.status not in _EXPIRABLE_STATUSES
                    or subscription.period_end > datetime.now(timezone.utc)
                ):
                    skipped_ids.append(tenant_id)
                    continue

                # Read just this flag rather than validating all preferences: one
                # bad unrelated value would otherwise fail this tenant every day.
                auto_pay = (tenant.preferences or {}).get("auto_pay_subscription") is True
                renewed = False

                # An expired trial is never auto-renewed: the tenant hasn't paid
                # yet, so it always falls back to past due and they buy a plan
                # themselves.
                if (
                    subscription.status == TenantSubscriptionStatus.ACTIVE
                    and auto_pay
                ):
                    try:
                        # Renews the SAME plan the tenant was already on - this
                        # reuses the exact lock/balance-check/expense/activate
                        # sequence the manual purchase endpoint uses, so auto-pay
                        # can't drift from what a human clicking "pay" would get.
                        await TenantSubscriptionService(uow).purchase_for_tenant(tenant_id, subscription.plan_id)
                        renewed = True
                    except BaseAppException as exc:
                        # purchase_for_tenant raises every domain error (insufficient
                        # balance, archived plan, ...) before changing anything, so
                        # it's safe to fall back to past due in this same transaction.
                        logger.warning(
                            f"Auto-renewal of plan {subscription.plan_id} failed for tenant {tenant_id} "
                            f"({exc.errorCode}); marking past due instead."
                        )

                if not renewed:
                    subscription.status = TenantSubscriptionStatus.PAST_DUE

            # celery_transaction_scope has committed by here - clear the cache only now.
            await delete_tenant_active(tenant_id)
            (renewed_ids if renewed else past_due_ids).append(tenant_id)
        except Exception:
            logger.exception(f"Failed to process expiring subscription for tenant {tenant_id}")
            failed_ids.append(tenant_id)

    logger.info(
        f"Subscription expiry pass done: renewed={renewed_ids} past_due={past_due_ids} "
        f"skipped={skipped_ids} failed={failed_ids}"
    )
