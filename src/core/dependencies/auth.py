from datetime import datetime, timezone

from fastapi import Request
from sqlalchemy import select

from src.core.auth.security import decode_token
from src.core.cache.permission_cache import get_staff_permissions
from src.core.cache.tenant_cache import (
    get_tenant_active,
    set_tenant_active,
    get_tenant_admin_active,
    set_tenant_admin_active,
    get_tenant_parent,
    set_tenant_parent,
)
from src.core.config import settings
from src.core.dependencies.context import set_current_staff_id
from src.database.session import SessionLocal
from src.exceptions.auth_exceptions import IncorrectCredentials, TenantIsInactive
from src.exceptions.staff_exceptions import StaffIsInactive
from src.repository.staff.staff_model import Staff
from src.repository.tenant.tenant_model import Tenant, TenantSubscriptions, TenantSubscriptionStatus

_ACTIVE_SUBSCRIPTION_STATUSES = (TenantSubscriptionStatus.ACTIVE, TenantSubscriptionStatus.TRIAL)
_INACTIVE_CACHE_TTL_SECONDS = 60

async def is_tenant_admin_active(tenant_id: int) -> bool:
    cached = await get_tenant_admin_active(tenant_id)
    if cached is not None:
        return cached

    async with SessionLocal() as session:
        result = await session.execute(select(Tenant.active).where(Tenant.id == tenant_id))
        active = bool(result.scalar_one_or_none())

    await set_tenant_admin_active(tenant_id, active, ttl = settings.REFRESH_TOKEN_EXPIRE_SECONDS)
    return active

async def _get_parent_id(tenant_id: int) -> int | None:
    found, parent_id = await get_tenant_parent(tenant_id)
    if found:
        return parent_id

    async with SessionLocal() as session:
        result = await session.execute(select(Tenant.parent_id).where(Tenant.id == tenant_id))
        parent_id = result.scalar_one_or_none()

    await set_tenant_parent(tenant_id, parent_id)
    return parent_id

async def is_tenant_active(tenant_id: int) -> bool:
    """
    Cache-first tenant active-status check; falls back to the database on a cache miss.
    A tenant is active only if it hasn't been manually disabled AND it has a
    subscription that is currently active/trialing and not past its period_end.

    Branches have no subscription of their own: a branch is active if it isn't
    disabled itself and its parent is active. Nothing is cached under the branch's
    own key, so clearing the parent's key is enough to update every branch.
    """
    parent_id = await _get_parent_id(tenant_id)
    if parent_id is not None:
        return await is_tenant_admin_active(tenant_id) and await is_tenant_active(parent_id)

    cached = await get_tenant_active(tenant_id)
    if cached is not None:
        return cached

    async with SessionLocal() as session:
        result = await session.execute(
            select(Tenant.active, TenantSubscriptions.status, TenantSubscriptions.period_end)
            .outerjoin(TenantSubscriptions, TenantSubscriptions.tenant_id == Tenant.id)
            .where(Tenant.id == tenant_id)
        )
        row = result.one_or_none()

    now = datetime.now(timezone.utc)
    active = (
        row is not None
        and row.active is True
        and row.status in _ACTIVE_SUBSCRIPTION_STATUSES
        and row.period_end is not None
        and row.period_end > now
    )

    if active:
        # Never let a cached "active" outlive the subscription itself - this is
        # what makes expiry exact, even if the Celery expiry task is late or fails.
        ttl = max(1, min(settings.REFRESH_TOKEN_EXPIRE_SECONDS, int((row.period_end - now).total_seconds())))
    else:
        # Keep "inactive" short-lived: if a cache clear after a purchase is ever
        # missed (e.g. Redis briefly down), a tenant who just paid is locked out
        # for at most this long instead of days.
        ttl = _INACTIVE_CACHE_TTL_SECONDS

    await set_tenant_active(tenant_id, active, ttl = ttl)
    return active

async def is_staff_active(staff_id: int) -> bool | None:
    """
    Cache-first staff active-status check (reuses the permissions cache entry
    from src/core/cache/permission_cache.py); falls back to the database on a
    cache miss. Returns None if the staff no longer exists.
    """
    cached = await get_staff_permissions(staff_id)
    if cached is not None and "active" in cached:
        return cached["active"]

    async with SessionLocal() as session:
        result = await session.execute(select(Staff.active).where(Staff.id == staff_id))
        return result.scalar_one_or_none()

async def get_current_staff(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if token is None:
        raise IncorrectCredentials()

    payload = decode_token(token)
    if payload is None: raise IncorrectCredentials()

    login: str = payload.get("sub")
    id: int = payload.get("id")
    tenant_id: int = payload.get("tenant_id")
    actor_id: int = payload.get("actor_id")

    if login is None or id is None or tenant_id is None: raise IncorrectCredentials()

    if not await is_tenant_admin_active(tenant_id):
        raise TenantIsInactive()

    active = await is_staff_active(id)
    if active is None: raise IncorrectCredentials()
    if not active: raise StaffIsInactive()

    set_current_staff_id(id, tenant_id, actor_id)

    return {
        "sub": login, 
        "id": id, 
        "tenant_id": tenant_id,
        "actor_id": actor_id
        }