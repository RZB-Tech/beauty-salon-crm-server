from fastapi import Request
from sqlalchemy import select

from src.core.auth.security import decode_token
from src.core.cache.permission_cache import get_staff_permissions
from src.core.cache.tenant_cache import get_tenant_active, set_tenant_active
from src.core.config import settings
from src.core.dependencies.context import set_current_staff_id
from src.database.session import SessionLocal
from src.exceptions.auth_exceptions import IncorrectCredentials, TenantIsInactive
from src.exceptions.staff_exceptions import StaffIsInactive
from src.repository.staff.staff_model import Staff
from src.repository.tenant.tenant_model import Tenant

async def is_tenant_active(tenant_id: int) -> bool:
    """Cache-first tenant active-status check; falls back to the database on a cache miss."""
    cached = await get_tenant_active(tenant_id)
    if cached is not None:
        return cached

    async with SessionLocal() as session:
        result = await session.execute(select(Tenant.active).where(Tenant.id == tenant_id))
        active = bool(result.scalar_one_or_none())

    await set_tenant_active(tenant_id, active, ttl = settings.REFRESH_TOKEN_EXPIRE_SECONDS)
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

    if not await is_tenant_active(tenant_id):
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