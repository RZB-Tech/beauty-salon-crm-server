from datetime import datetime, timezone
import json

from fastapi import APIRouter, Depends, Request, status
from sse_starlette import EventSourceResponse
from src.core.dependencies.uow import UnitOfWork, get_uow_with_context, make_service_dependency
from src.core.utils import sse_manager
from src.core.utils.sse_publisher import publish_notification
from src.schemas.base import PaginatedResponseSchema, RequestAllObject
from src.schemas.notification.create import NotificationCreateSchema
from src.schemas.notification.response import NotificationResponseSchema
from src.services.notification_service import NotificationService
from src.core.utils.sse_manager import sse_manager
from src.core.config import settings
import redis.asyncio as aioredis

router = APIRouter()

get_notification_service = make_service_dependency(NotificationService)

@router.post(
    "/", 
    response_model=NotificationResponseSchema, 
    status_code=status.HTTP_201_CREATED,
)
async def create(data: NotificationCreateSchema,
                 notificationService: NotificationService = Depends(get_notification_service)):
    return await notificationService.create(data)

@router.post(
    "/get-all",
    response_model=PaginatedResponseSchema[NotificationResponseSchema], 
    status_code = 200,
)
async def get_all(params: RequestAllObject,
                 notificationService: NotificationService = Depends(get_notification_service)):
    return await notificationService.get_all(params)

@router.get(
    "/{id}",
    response_model=NotificationResponseSchema, 
    status_code = 200
)
async def get(id: int,
                 notificationService: NotificationService = Depends(get_notification_service)):
    return await notificationService.get(id)

@router.delete(
    "/{id}",
    response_model = NotificationResponseSchema,
    status_code = 200
)
async def archive(id: int,
                 notificationService: NotificationService = Depends(get_notification_service)):
    return await notificationService.archive(id)

@router.delete(
    "/{id}",
    status_code = 204
)
async def delete(id: int,
                 notificationService: NotificationService = Depends(get_notification_service)):
    return await notificationService.delete(id)

@router.get("/stream/{client_id}")
async def notification_stream(client_id: int, request: Request):

    async def event_generator():
        r = aioredis.from_url(settings.REDIS_BROKER)
        pubsub = r.pubsub()
        await pubsub.subscribe(f"notifications:{client_id}")

        try:
            yield {
                "event": "connected",
                "data": json.dumps({"message": "connected"}),
            }

            async for message in pubsub.listen():
                if await request.is_disconnected():
                    break
                if message["type"] == "message":
                    yield {
                        "event": "notification",
                        "data": message["data"].decode(),
                    }
        finally:
            await pubsub.unsubscribe(f"notifications:{client_id}")
            await pubsub.aclose()
            await r.aclose()

    return EventSourceResponse(event_generator())

@router.post("/stream/{client_id}/test")
async def test_notification_stream(client_id: int):
    payload = {
        "id": 999,
        "title": "Test notification",
        "body": "If you see this, SSE + Redis pub/sub is working!",
        "type": "other",
        "scheduled_at": datetime.now(timezone.utc).isoformat(),
    }
    await publish_notification(client_id, payload)
    return {"published_to": f"notifications:{client_id}", "payload": payload}