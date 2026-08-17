from src.repository.notification.notification_model import NotificationStatus, NotificationType
from datetime import datetime

from src.schemas.base import BaseResponseSchema

class NotificationResponseSchema(BaseResponseSchema):
    client_id: int | None = None
    title: str | None = None
    body: str
    type: NotificationType
    status: NotificationStatus
    notes: str | None = None
    scheduled_at: datetime
    delivered_at: datetime | None = None