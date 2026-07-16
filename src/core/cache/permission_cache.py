import json
import logging

from redis.asyncio import Redis
from redis.exceptions import RedisError

from src.core.config import settings

logger = logging.getLogger(__name__)

_redis_client: Redis | None = None

def get_redis_client() -> Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis.from_url(
            settings.REDIS_BACKEND,
            decode_responses = True,
            socket_connect_timeout = 1,
            socket_timeout = 1,
        )
    return _redis_client

def _key(staff_id: int) -> str:
    return f"staff:{staff_id}:permissions"

async def set_staff_permissions(staff_id: int, staff_type: str, permissions: list[int], ttl: int) -> None:
    try:
        payload = json.dumps({"staff_type": staff_type, "permissions": permissions})
        await get_redis_client().set(_key(staff_id), payload, ex = ttl)
    except RedisError:
        logger.warning("Redis unavailable, skipping permissions cache write for staff %s", staff_id)

async def get_staff_permissions(staff_id: int) -> dict | None:
    try:
        raw = await get_redis_client().get(_key(staff_id))
        return json.loads(raw) if raw else None
    except RedisError:
        logger.warning("Redis unavailable, falling back to database for staff %s permissions", staff_id)
        return None

async def delete_staff_permissions(staff_id: int) -> None:
    try:
        await get_redis_client().delete(_key(staff_id))
    except RedisError:
        logger.warning("Redis unavailable, could not clear permissions cache for staff %s", staff_id)