from enum import StrEnum

from sqlalchemy import func, or_, select

from src.core.dependencies.uow import UnitOfWork
from src.exceptions.auth_exceptions import TenantIsInactive
from src.exceptions.tenant_exceptions import TenantLimitExceeded, TenantNotFound
from src.repository.client.client_model import Client
from src.repository.staff.staff_model import Staff
from src.repository.tenant.tenant_model import Tenant


class TenantLimit(StrEnum):
    """Values match both the SubscriptionPlan column and TenantAddon.limit_key."""
    BRANCHES = "max_branches"
    USERS = "max_users"
    CLIENTS = "max_clients"

# Advisory lock ids, also the order locks are taken in - always ascending, so
# two requests needing several limits can't deadlock each other.
_LOCK_IDS = {TenantLimit.BRANCHES: 1, TenantLimit.USERS: 2, TenantLimit.CLIENTS: 3}


async def ensure_tenant_capacity(uow: UnitOfWork, tenant_id: int, required: dict[TenantLimit, int]) -> None:
    """
    Raises TenantLimitExceeded if adding `required` more of each resource would go
    over the organization's subscription limits. Limits are shared by the whole
    organization - the parent tenant and all its branches - and come from the
    parent's plan plus its unexpired addons. A limit of None on the plan means
    unlimited.

    Must be called in the same transaction that creates the resources: it takes
    an advisory lock per organization and limit, held until that transaction
    ends, so two concurrent creations can't both pass the count.
    """
    tenant = await uow.tenants.get(id = tenant_id)
    if tenant is None: raise TenantNotFound(tenant_id)
    root_id = tenant.parent_id or tenant.id

    for limit in sorted(required, key = _LOCK_IDS.__getitem__):
        await uow.db.execute(select(func.pg_advisory_xact_lock(_LOCK_IDS[limit], root_id)))

    subscription = await uow.tenantSubscriptions.get_by_tenant(root_id)
    if subscription is None: raise TenantIsInactive()
    plan = await uow.subscriptionsPlans.get(subscription.plan_id)

    for limit, adding in required.items():
        base = getattr(plan, limit.value)
        if base is None:
            continue
        allowed = base + await uow.tenantAddons.get_effective_limit(root_id, limit.value)
        used = await _count_used(uow, root_id, limit)
        if used + adding > allowed:
            raise TenantLimitExceeded(limit.value, allowed, used)


async def _count_used(uow: UnitOfWork, root_id: int, limit: TenantLimit) -> int:
    if limit == TenantLimit.BRANCHES:
        # Only real branches count - the parent itself isn't one, so
        # max_branches = 3 allows 3 branches besides the parent.
        stmt = select(func.count()).select_from(Tenant).where(Tenant.parent_id == root_id)
        return (await uow.db.execute(stmt)).scalar_one()

    model = Staff if limit == TenantLimit.USERS else Client
    organization = select(Tenant.id).where(or_(Tenant.id == root_id, Tenant.parent_id == root_id))
    # Every row counts, archived and inactive ones included - neither frees a slot.
    # skip_tenant_filter: the request is scoped to one tenant, but the count spans
    # the parent and every branch.
    stmt = (
        select(func.count())
        .select_from(model)
        .where(model.tenant_id.in_(organization))
        .execution_options(skip_tenant_filter = True)
    )
    return (await uow.db.execute(stmt)).scalar_one()
