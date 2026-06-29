from pydantic import BaseModel, Field
from src.repository.notification.notification_model import NotificationType
from datetime import datetime

class NotificationCreateSchema(BaseModel):
    client_id: int | None = Field(None, ge = 1)
    title: str | None = Field(None, max_length = 50)
    body: str
    type: NotificationType = NotificationType.REMINDER
    scheduled_at: datetime