from fastapi import HTTPException, Request, WebSocket, status
from sqlalchemy import select

from src.core.auth.security import decode_token
from src.core.cache.tenant_cache import get_tenant_active, set_tenant_active
from src.core.config import settings
from src.core.dependencies.context import set_current_staff_id
from src.database.session import SessionLocal
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

async def get_current_staff(request: Request) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные"
    )

    token = request.cookies.get("access_token")
    if token is None:
        raise credentials_exception

    payload = decode_token(token)
    if payload is None: raise credentials_exception

    login: str = payload.get("sub")
    id: int = payload.get("id")
    tenant_id: int = payload.get("tenant_id")
    actor_id: int = payload.get("actor_id")

    if login is None or id is None or tenant_id is None: raise credentials_exception

    if not await is_tenant_active(tenant_id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail = "Организация деактивирована")

    set_current_staff_id(id, tenant_id, actor_id)

    return {
        "sub": login, 
        "id": id, 
        "tenant_id": tenant_id,
        "actor_id": actor_id
        }