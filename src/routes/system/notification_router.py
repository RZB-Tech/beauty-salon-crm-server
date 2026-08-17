from datetime import datetime, timezone
import json
import logging

from fastapi import APIRouter, Depends, Request, status
from redis.exceptions import RedisError
from sse_starlette import EventSourceResponse
from src.core.dependencies.auth import get_current_staff
from src.core.dependencies.permissions import require_permission
from src.core.dependencies.uow import make_service_dependency
from src.core.permissions import PermissionCode
from src.schemas.base import PaginatedResponseSchema, RequestAllObject
from src.schemas.notification.create import NotificationCreateSchema
from src.schemas.notification.read import NotificationReadSchema
from src.schemas.notification.response import NotificationResponseSchema
from src.services.client.notification_service import NotificationService
from src.core.config import settings
import redis.asyncio as aioredis

logger = logging.getLogger(__name__)

router = APIRouter()

get_notification_service = make_service_dependency(NotificationService)

@router.post(
    "",
    response_model=NotificationResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary = "Создать уведомление",
    description = "Создает уведомление (например, напоминание клиенту о записи), запланированное к отправке на время `scheduled_at`.",
    dependencies=[Depends(require_permission([PermissionCode.NOTIFICATION_CREATE]))]
)
async def create(data: NotificationCreateSchema,
                 notificationService: NotificationService = Depends(get_notification_service)):
    return await notificationService.create(data)

@router.post(
    "/get-all",
    response_model=PaginatedResponseSchema[NotificationResponseSchema],
    status_code = 200,
    summary = "Получить все уведомления",
    description = "Возвращает постраничный список уведомлений с поддержкой фильтрации.",
    dependencies=[Depends(require_permission([PermissionCode.NOTIFICATION_READ]))]
)
async def get_all(params: RequestAllObject,
                 notificationService: NotificationService = Depends(get_notification_service)):
    return await notificationService.get_all(params)

@router.get(
    "/stream",
    summary = "Поток уведомлений (SSE)",
    description = "Открывает Server-Sent Events соединение и передает уведомления текущему сотруднику в реальном времени по мере их поступления.",
    dependencies=[Depends(require_permission([PermissionCode.NOTIFICATION_READ]))]
)
async def notification_stream(
    request: Request,
    current_staff: dict = Depends(get_current_staff)):
    async def event_generator():
        staffID = current_staff["id"]
        r = aioredis.from_url(settings.REDIS_BROKER)
        pubsub = r.pubsub()

        try:
            await pubsub.subscribe(f"notifications:{staffID}")
        except RedisError:
            logger.warning("Redis unavailable, closing notification stream for staff %s", staffID)
            await r.aclose()
            yield {
                "event": "error",
                "data": json.dumps({"message": "notifications unavailable"}),
                "retry": 15000
            }
            return

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
        except RedisError:
            logger.warning("Redis connection lost, closing notification stream for staff %s", staffID)
            yield {
                "event": "error",
                "data": json.dumps({"message": "notifications unavailable"}),
                "retry": 15000,
            }
        finally:
            try:
                await pubsub.unsubscribe(f"notifications:{staffID}")
                await pubsub.aclose()
                await r.aclose()
            except RedisError:
                pass

    return EventSourceResponse(event_generator())

@router.get(
    "/{id}",
    response_model=NotificationResponseSchema,
    status_code = 200,
    summary = "Получить уведомление по ID",
    dependencies=[Depends(require_permission([PermissionCode.NOTIFICATION_READ]))]
)
async def get(id: int,
                 notificationService: NotificationService = Depends(get_notification_service)):
    return await notificationService.get(id)

@router.post(
    "/read",
    response_model = NotificationResponseSchema,
    status_code = 200,
    summary = "Отметить уведомление прочитанным",
    description = "Переводит уведомление в статус `read`. Уже прочитанное уведомление отметить повторно нельзя.",
    dependencies=[Depends(require_permission([PermissionCode.NOTIFICATION_CREATE]))]
)
async def read(data: NotificationReadSchema,
               notificationService: NotificationService = Depends(get_notification_service)):
    return await notificationService.read(data)

@router.post(
    "/{id}/cancel",
    response_model = NotificationResponseSchema,
    status_code = 200,
    summary = "Отменить уведомление",
    description = "Переводит запланированное уведомление в статус `cancelled`, чтобы оно не было отправлено. Уже отмененное уведомление отменить повторно нельзя.",
    dependencies=[Depends(require_permission([PermissionCode.NOTIFICATION_CANCEL]))]
)
async def cancel(id: int,
                 notificationService: NotificationService = Depends(get_notification_service)):
    return await notificationService.cancel(id)