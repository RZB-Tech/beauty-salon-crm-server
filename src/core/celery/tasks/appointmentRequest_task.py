import asyncio
import logging
from datetime import datetime, timezone

from src.core.celery.celeryApp import celery_app
from src.core.celery.tasks.notification_task import celery_transaction_scope
from src.core.dependencies.uow import UnitOfWork

logger = logging.getLogger(__name__)

@celery_app.task(name="cancel_past_due_appointment_requests")
def cancel_past_due_appointment_requests():
    asyncio.run(_cancel_past_due())

async def _cancel_past_due():
    # Across all tenants: the Celery session has no tenant filter attached
    async with celery_transaction_scope():
        uow = UnitOfWork()
        cancelled = await uow.appointmentRequests.cancel_past_due(datetime.now(timezone.utc))
        if cancelled:
            logger.info(f"Cancelled {cancelled} past due appointment request(s).")
