import logging

from redis.exceptions import RedisError

from src.core.cache.permission_cache import get_redis_client

logger = logging.getLogger(__name__)

MAX_FAILED_ATTEMPTS = 3
FAILED_ATTEMPTS_TTL = 900

def _key(login: str) -> str:
    return f"admin_login:{login}:failed_attempts"

async def register_failed_login(login: str) -> int:
    try:
        client = get_redis_client()
        key = _key(login)
        attempts = await client.incr(key)
        if attempts == 1:
            await client.expire(key, FAILED_ATTEMPTS_TTL)
        return attempts
    except RedisError:
        logger.warning("Redis unavailable, could not track failed login attempts for %s", login)
        return 0

async def reset_failed_login(login: str) -> None:
    try:
        await get_redis_client().delete(_key(login))
    except RedisError:
        logger.warning("Redis unavailable, could not reset failed login attempts for %s", login)
