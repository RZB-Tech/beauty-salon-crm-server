import asyncio
import logging
from datetime import datetime, timezone

from src.core.celery.celeryApp import celery_app
from src.core.celery.tasks.notification_task import celery_transaction_scope
from src.core.dependencies.uow import UnitOfWork
from src.services.miniApp.clientNotifications import auto_cancelled_text, notify_telegram_client

logger = logging.getLogger(__name__)

@celery_app.task(name="cancel_past_due_appointment_requests")
def cancel_past_due_appointment_requests():
    asyncio.run(_cancel_past_due())

async def _cancel_past_due():
    # Across all tenants: the Celery session has no tenant filter attached
    async with celery_transaction_scope():
        uow = UnitOfWork()
        cancelled = await uow.appointmentRequests.cancel_past_due(datetime.now(timezone.utc))
        if not cancelled:
            return
        telegram_ids = await uow.globalClients.get_telegram_user_ids(list({gid for _, gid, _ in cancelled}))
        tenant_names = await uow.tenants.get_names(list({tid for tid, _, _ in cancelled}))

    # Committed by here - only now tell the clients
    logger.info(f"Cancelled {len(cancelled)} past due appointment request(s).")
    for tenant_id, global_client_id, start in cancelled:
        telegram_user_id = telegram_ids.get(global_client_id)
        if telegram_user_id is not None:
            notify_telegram_client(telegram_user_id, auto_cancelled_text(tenant_names.get(tenant_id, ""), start))
