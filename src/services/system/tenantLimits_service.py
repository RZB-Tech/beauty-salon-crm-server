from dataclasses import dataclass
from enum import StrEnum

from sqlalchemy import func, select

from src.core.dependencies.uow import UnitOfWork
from src.exceptions.tenant_exceptions import TenantLimitExceeded
from src.repository.client.client_model import Client
from src.repository.staff.staff_model import Staff


class TenantLimit(StrEnum):
    """Values match both the SubscriptionPlan column and TenantAddon.limit_key."""
    USERS = "max_users"
    CLIENTS = "max_clients"

# Advisory lock ids, also the order locks are taken in - always ascending, so
# two requests needing several limits can't deadlock each other.
_LOCK_IDS = {TenantLimit.USERS: 2, TenantLimit.CLIENTS: 3}


@dataclass
class LimitUsage:
    limit: TenantLimit
    plan: int | None       # from the plan; None = unlimited
    addons: int            # extra capacity from unexpired addons
    allowed: int | None    # plan + addons; None = unlimited
    used: int


async def _usage(uow: UnitOfWork, tenant_id: int, plan, limit: TenantLimit) -> LimitUsage:
    # No plan (no subscription yet) means no base capacity - only addons count.
    base = getattr(plan, limit.value) if plan is not None else 0
    addons = await uow.tenantAddons.get_effective_limit(tenant_id, limit.value)
    return LimitUsage(
        limit = limit,
        plan = base,
        addons = addons,
        allowed = None if base is None else base + addons,
        used = await _count_used(uow, tenant_id, limit),
    )


async def _get_plan(uow: UnitOfWork, tenant_id: int):
    subscription = await uow.tenantSubscriptions.get_by_tenant(tenant_id)
    return await uow.subscriptionsPlans.get(subscription.plan_id) if subscription else None


async def get_limits_usage(uow: UnitOfWork, tenant_id: int) -> tuple[int | None, list[LimitUsage]]:
    """
    (plan_id, usage of every limit) for `tenant_id` - the same numbers
    ensure_tenant_capacity enforces. Read-only, takes no locks.
    """
    plan = await _get_plan(uow, tenant_id)
    return (
        plan.id if plan else None,
        [await _usage(uow, tenant_id, plan, limit) for limit in TenantLimit],
    )


async def ensure_tenant_capacity(uow: UnitOfWork, tenant_id: int, required: dict[TenantLimit, int]) -> None:
    """
    Raises TenantLimitExceeded if adding `required` more of each resource to
    `tenant_id` would go over its limits: its own plan plus its own unexpired
    addons. Every tenant - parent or branch - has its own subscription and
    limits; nothing is shared. A limit of None on the plan means unlimited;
    no subscription means no capacity beyond addons.

    Must be called in the same transaction that creates the resources: it takes
    an advisory lock per tenant and limit, held until that transaction ends, so
    two concurrent creations can't both pass the count.
    """
    for limit in sorted(required, key = _LOCK_IDS.__getitem__):
        await uow.db.execute(select(func.pg_advisory_xact_lock(_LOCK_IDS[limit], tenant_id)))

    plan = await _get_plan(uow, tenant_id)

    for limit, adding in required.items():
        usage = await _usage(uow, tenant_id, plan, limit)
        if usage.allowed is not None and usage.used + adding > usage.allowed:
            raise TenantLimitExceeded(limit.value, usage.allowed, usage.used)


async def _count_used(uow: UnitOfWork, tenant_id: int, limit: TenantLimit) -> int:
    model = Staff if limit == TenantLimit.USERS else Client
    # Every row counts, archived and inactive ones included - neither frees a slot.
    # skip_tenant_filter: the caller may act on another tenant (a parent adding a
    # branch's admin), so filter explicitly by the tenant being checked instead.
    stmt = (
        select(func.count())
        .select_from(model)
        .where(model.tenant_id == tenant_id)
        .execution_options(skip_tenant_filter = True)
    )
    return (await uow.db.execute(stmt)).scalar_one()
