from pydantic import BaseModel, ConfigDict, Field
from src.repository.notification.notification_model import NotificationType
from datetime import datetime

class NotificationCreateSchema(BaseModel):
    client_id: int | None = Field(None, ge = 1)
    title: str | None = Field(None, max_length = 50)
    body: str
    type: NotificationType = NotificationType.REMINDER
    scheduled_at: datetime

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "client_id": 1,
            "title": "Напоминание о записи",
            "body": "Напоминаем, что завтра в 10:00 у вас запись",
            "type": "reminder",
            "scheduled_at": "2026-08-09T18:00:00"
        }
    })