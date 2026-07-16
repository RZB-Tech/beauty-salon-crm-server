from datetime import datetime, timezone
import json

from fastapi import APIRouter, Depends, Request, status
from sse_starlette import EventSourceResponse
from src.core.dependencies.auth import get_current_staff
from src.core.dependencies.permissions import require_permission
from src.core.dependencies.uow import make_service_dependency
from src.core.permissions import PermissionCode
from src.schemas.base import PaginatedResponseSchema, RequestAllObject
from src.schemas.notification.create import NotificationCreateSchema
from src.schemas.notification.response import NotificationResponseSchema
from src.services.client.notification_service import NotificationService
from src.core.config import settings
import redis.asyncio as aioredis

router = APIRouter()

get_notification_service = make_service_dependency(NotificationService)

@router.post(
    "",
    response_model=NotificationResponseSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission([PermissionCode.NOTIFICATION_CREATE]))]
)
async def create(data: NotificationCreateSchema,
                 notificationService: NotificationService = Depends(get_notification_service)):
    return await notificationService.create(data)

@router.post(
    "/get-all",
    response_model=PaginatedResponseSchema[NotificationResponseSchema],
    status_code = 200,
    dependencies=[Depends(require_permission([PermissionCode.NOTIFICATION_READ]))]
)
async def get_all(params: RequestAllObject,
                 notificationService: NotificationService = Depends(get_notification_service)):
    return await notificationService.get_all(params)

@router.get(
    "/stream",
    dependencies=[Depends(require_permission([PermissionCode.NOTIFICATION_READ]))]
)
async def notification_stream(
    request: Request,
    current_staff: dict = Depends(get_current_staff)):
    async def event_generator():
        staffID = current_staff["id"]
        r = aioredis.from_url(settings.REDIS_BROKER)
        pubsub = r.pubsub()
        await pubsub.subscribe(f"notifications:{staffID}")

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
            await pubsub.unsubscribe(f"notifications:{staffID}")
            await pubsub.aclose()
            await r.aclose()

    return EventSourceResponse(event_generator())

@router.get(
    "/{id}",
    response_model=NotificationResponseSchema,
    status_code = 200,
    dependencies=[Depends(require_permission([PermissionCode.NOTIFICATION_READ]))]
)
async def get(id: int,
                 notificationService: NotificationService = Depends(get_notification_service)):
    return await notificationService.get(id)

@router.delete(
    "/{id}",
    response_model = NotificationResponseSchema,
    status_code = 200,
    dependencies=[Depends(require_permission([PermissionCode.NOTIFICATION_ARCHIVE]))]
)
async def archive(id: int,
                 notificationService: NotificationService = Depends(get_notification_service)):
    return await notificationService.archive(id)

@router.delete(
    "/{id}",
    status_code = 204,
    dependencies=[Depends(require_permission([PermissionCode.NOTIFICATION_DELETE]))]
)
async def delete(id: int,
                 notificationService: NotificationService = Depends(get_notification_service)):
    return await notificationService.delete(id)