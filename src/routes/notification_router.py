from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from src.core.dependencies.uow import UnitOfWork, get_uow_with_context
from src.schemas.base import PaginatedResponseSchema, RequestAllObject
from src.schemas.notification.create import NotificationCreateSchema
from src.schemas.notification.response import NotificationResponseSchema
from src.services.notification_service import NotificationService
from src.core.utils.ws_connection_manage import manager
from src.core.dependencies.auth import get_current_staff_ws

router = APIRouter()

def get_notification_service(uow: UnitOfWork = Depends(get_uow_with_context)) -> NotificationService:
    return NotificationService(uow=uow)

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

