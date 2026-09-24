from celery import Celery
from celery.schedules import crontab
from src.core.config import settings

celery_app = Celery(
    "notifications",
    broker = settings.REDIS_BROKER,
    backend = settings.REDIS_BACKEND,
    include = [
        "src.core.celery.tasks.notification_task",
        "src.core.celery.tasks.tenantSubscription_task",
    ],
)

celery_app.conf.update(
    timezone="UTC",
    task_ignore_result=True,
    beat_schedule={
        "poll-notifications-every-minute": {
            "task": "poll_and_deliver_notification",
            "schedule": 60.0,  # seconds
        },
        # A fixed time of day, not an 86400s interval: an interval restarts
        # counting whenever celery-beat restarts.
        "expire-tenant-subscriptions-daily": {
            "task": "expire_tenant_subscriptions",
            "schedule": crontab(hour = 0, minute = 5),  # 00:05 UTC
        },
    },
)