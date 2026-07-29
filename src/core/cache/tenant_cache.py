import logging

from redis.exceptions import RedisError

from src.core.cache.permission_cache import get_redis_client

logger = logging.getLogger(__name__)

def _key(tenant_id: int) -> str:
    return f"tenant:{tenant_id}:active"

async def set_tenant_active(tenant_id: int, active: bool, ttl: int) -> None:
    try:
        await get_redis_client().set(_key(tenant_id), "1" if active else "0", ex = ttl)
    except RedisError:
        logger.warning("Redis unavailable, skipping active-status cache write for tenant %s", tenant_id)

async def get_tenant_active(tenant_id: int) -> bool | None:
    try:
        raw = await get_redis_client().get(_key(tenant_id))
        return raw == "1" if raw is not None else None
    except RedisError:
        logger.warning("Redis unavailable, falling back to database for tenant %s active status", tenant_id)
        return None

async def delete_tenant_active(tenant_id: int) -> None:
    try:
        await get_redis_client().delete(_key(tenant_id))
    except RedisError:
        logger.warning("Redis unavailable, could not clear active-status cache for tenant %s", tenant_id)
