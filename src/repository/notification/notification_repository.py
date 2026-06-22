from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from src.core.utils.model_filter import apply_dynamic_filters
from src.database.base import BaseRepository
from src.repository.notification.notification_model import Notification
from src.schemas.base import RequestAllObject

class NotificationRepository(BaseRepository):
    async def create(self, notification: Notification) -> Notification:
        self.db.add(notification)
        await self.db.flush()
        await self.db.refresh(notification)
        return notification
    
    async def get(self, id: int) -> Notification | None:
        return await self.db.get(Notification, id)
    
    async def get_all(self, data: RequestAllObject) -> tuple[list[Notification], int]:
        count_stmt = select(func.count()).select_from(Notification)
        stmt = select(Notification)
        count_stmt = apply_dynamic_filters(count_stmt, Notification, data.filters)
        stmt = apply_dynamic_filters(stmt, Notification, data.filters)
        total_items = await self.db.scalar(count_stmt) or 0
        offset_value = (data.page - 1) * data.pageSize
        stmt = stmt.offset(offset_value).limit(data.pageSize)
        result = await self.db.execute(stmt)
        items = list(result.scalars().all())
        return items, total_items
    
    async def archive(self, id: int) -> Notification | None:
        obj = await self.db.get(Notification, id)

        if not obj: return None
        obj.archived = True

        await self.db.flush()
        await self.db.refresh(obj)
        return obj
    
    async def delete(self, id: int) -> bool:
        obj = await self.db.get(Notification, id)
        if not obj: return False

        await self.db.delete(obj)
        return True
    
    async def deliver(self, id: int, delivered_at: datetime) -> Notification:
        obj = await self.db.get(Notification, id)
        if not obj: return None

        obj.delivered_at = delivered_at
        await self.db.flush()
        await self.db.refresh(obj)
        return obj