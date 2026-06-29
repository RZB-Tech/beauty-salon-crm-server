import json
import redis.asyncio as aioredis
from src.core.config import settings

async def publish_notification(staff_id: int, payload: dict) -> None:
    r = aioredis.from_url(settings.REDIS_BROKER)
    received = await r.publish(f"notifications:{staff_id}", json.dumps(payload))
    await r.aclose()
    return received