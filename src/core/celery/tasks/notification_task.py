import asyncio
import logging

from src.core.celery.celeryApp import celery_app
from src.core.celery.session import celery_transaction_scope
from src.core.dependencies.uow import UnitOfWork
from src.core.utils.sse_publisher import publish_notification

logger = logging.getLogger(__name__)

@celery_app.task(name="poll_and_deliver_notification")
def poll_and_deliver():
    asyncio.run(_poll_and_deliver())


async def _poll_and_deliver():
    async with celery_transaction_scope():
        uow = UnitOfWork()
        pending = await uow.notifications.claim_pending()

        if not pending:
            logger.info("No pending notifications.")
            return

        logger.info(f"Claimed {len(pending)} notification(s).")
        failed_ids = []

        for notification in pending:
            try:
                payload = {
                    "id": notification.id,
                    "title": notification.title,
                    "body": notification.body,
                    "type": notification.type.value,
                    "scheduled_at": notification.scheduled_at.isoformat(),
                }
                subscribers = await publish_notification(notification.created_by, payload)

                if not subscribers:  # catches both 0 and None
                    failed_ids.append(notification.id)
                    logger.warning(f"Notification {notification.id}: no listeners, will retry.")
                else:
                    logger.info(f"Notification {notification.id} delivered to {subscribers} subscriber(s).")

            except Exception as e:
                failed_ids.append(notification.id)
                logger.error(f"Failed to deliver notification {notification.id}: {e}")

        if failed_ids:
            await uow.notifications.revert_claim(failed_ids)