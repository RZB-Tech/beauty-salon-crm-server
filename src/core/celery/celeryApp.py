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
        # Access ends exactly at period_end (see has_active_subscription), so this has
        # to run often: auto-pay tenants are locked out from period_end until
        # the next run renews them. The task only selects already-expired rows
        # and re-checks each under lock, so frequent runs are cheap and safe.
        "expire-tenant-subscriptions": {
            "task": "expire_tenant_subscriptions",
            "schedule": crontab(minute = "*/10"),
        },
    },
)