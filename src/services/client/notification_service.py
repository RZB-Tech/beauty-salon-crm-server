from datetime import datetime, timezone
import math
from fastapi import HTTPException, status
from src.core.dependencies.uow import UnitOfWork
from src.core.utils import sse_manager
from src.repository.notification.notification_model import Notification, NotificationStatus
from src.schemas.base import RequestAllObject
from src.schemas.notification.create import NotificationCreateSchema
from src.core.utils.sse_manager import sse_manager

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
                detail = f"Уведомление с ID {id} не найден"
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

    async def read(self, id: int) -> Notification:
        notification = await self.uow.notifications.get(id)
        if notification is None: raise HTTPException(404, f"Уведомление с ID {id} не найдено")
        if notification.read: raise HTTPException(400, f"Уведомление уже прочитано")

        result = await self.uow.notifications.update(id, status = NotificationStatus.READ)
        if result is None: raise HTTPException(500, "Произошла ошибка при попытке обновить запись")
        return result
    
    async def archive(self, id: int) -> Notification:
        result = await self.uow.notifications.archive(id)
        if result is None: raise HTTPException(500, "Не получилось обновить запись")
        return result
    
    async def cancel(self, id: int) -> Notification:
        notification = await self.uow.notifications.get(id)
        if notification is None: raise HTTPException(404, f"Уведомление с ID {id} не найдено")
        if notification.cancelled: raise HTTPException(400, f"Уведомление уже отменено")

        result = await self.uow.notifications.update(id, status = NotificationStatus.CANCELLED)
        if result is None: raise HTTPException(500, "Произошла ошибка при попытке обновить запись")
        return result
    
    async def deliver(self, notification: Notification) -> None:
        staff = await self.uow.staffs.get(notification.created_by)
        if staff is None:
            return

        payload = {
            "id": notification.id,
            "title": notification.title,
            "body": notification.body,
            "type": notification.type,
            "scheduled_at": notification.scheduled_at.isoformat(),
        }

        was_delivered = await sse_manager.send(staff.id, payload)

        if was_delivered:
            await self.uow.notifications.deliver(
                notification.id,
                datetime.now(timezone.utc),
            )