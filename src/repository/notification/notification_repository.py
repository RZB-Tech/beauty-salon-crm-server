from datetime import datetime, timezone

import logging
from sqlalchemy import and_, func, select, update
from src.core.utils.model_filter import apply_dynamic_filters
from src.database.base import BaseRepository
from src.repository.notification.notification_model import Notification
from src.schemas.base import RequestAllObject

logger = logging.getLogger(__name__)

class NotificationRepository(BaseRepository[Notification]):
    async def create(self, notification: Notification) -> Notification:
        self.db.add(notification)
        await self.db.flush()
        await self.db.refresh(notification)
        return notification
    
    async def get_all(self, data: RequestAllObject) -> tuple[list[Notification], int]:
        count_stmt = select(func.count()).select_from(Notification)
        stmt = select(Notification)
        count_stmt = apply_dynamic_filters(count_stmt, Notification, data.filters)
        stmt = apply_dynamic_filters(stmt, Notification, data.filters)
        total_items = await self.db.scalar(count_stmt) or 0
        offset_value = (data.page - 1) * data.pageSize
        stmt = stmt.offset(offset_value).limit(data.pageSize)
        result = await self.db.execute(stmt)
        items = result.scalars().all()
        return items, total_items
    
    async def deliver(self, id: int, delivered_at: datetime) -> Notification:
        obj = await self.get(id)
        if not obj: return None

        obj.delivered_at = delivered_at
        await self.db.flush()
        await self.db.refresh(obj)
        return obj
    
    async def claim_pending(self) -> list[Notification]:
        now = datetime.now(timezone.utc)

        stmt = (
            update(Notification)
            .where(
                and_(
                    Notification.delivered_at.is_(None),
                    Notification.archived != True,
                    Notification.scheduled_at <= now,
                )
            )
            .values(delivered_at=now)
            .returning(Notification)  # ← return full model, not just id
            .execution_options(synchronize_session=False)
        )
        result = await self.db.execute(stmt)
        items = result.scalars().all()
        return items
    
    async def revert_claim(self, ids: list[int]) -> None:
        """Reset delivered_at so the next poll retries these."""
        stmt = (
            update(Notification)
            .where(Notification.id.in_(ids))
            .values(delivered_at=None)
        )
        await self.db.execute(stmt)