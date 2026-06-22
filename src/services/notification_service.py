from datetime import datetime, timezone
import math
from fastapi import HTTPException, status
from src.core.decorators.requireID import require_exists
from src.core.dependencies.uow import UnitOfWork
from src.repository.notification.notification_model import Notification
from src.schemas.base import RequestAllObject
from src.schemas.notification.create import NotificationCreateSchema
from src.core.utils.ws_connection_manage import manager as wsManager

class NotificationService():
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create(self, data: NotificationCreateSchema) -> Notification:
        notificationData = data.model_dump()
        newNotification = Notification(**notificationData)
        return await self.uow.notifications.create(newNotification)
    
    async def get(self, id: int) -> Notification:
        result = await self.uow.notifications.get(id)
        if not result:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"Notification category with id {id} not found"
            )
        return result
    
    async def get_many(self, ids: list[int]) -> Notification:
        return await self.uow.notifications.get_by_ids(ids)
    
    async def get_all(self, data: RequestAllObject) -> dict:
        items, total_items = await self.uow.notifications.get_all(data)

        total_pages = math.ceil(total_items / data.pageSize) if data.pageSize > 0 else 0
        
        return {
            "items": items,
            "page": data.page,
            "pageSize": data.pageSize,
            "totalItems": total_items,
            "totalPages": total_pages
        }
    
    async def archive(self, id: int) -> Notification:
        return await self.uow.notifications.archive(id)

    async def delete(self, id: int) -> bool:
        return await self.uow.notifications.delete(id)
    
    async def deliver(self, notification: Notification) -> None:
        staffID = self.uow.staffs.get(notification.created_by)
        if staffID is None: return 

        was_delivered = await wsManager.send(notification, staffID)
        
        if was_delivered:
            await self.uow.notifications.deliver(
                notification.id,
                datetime.now(timezone.utc),
            )
    