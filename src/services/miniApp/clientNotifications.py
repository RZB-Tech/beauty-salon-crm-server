"""Messages to mini app clients about their appointment requests, sent by the mini app's bot."""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Times are UTC for now - tenant timezones aren't supported yet
def _time(value: datetime) -> str:
    return f"{value:%d.%m.%Y %H:%M} (UTC)"

def confirmed_text(tenant_name: str, start: datetime) -> str:
    return f"✅ Ваша заявка на запись в «{tenant_name}» подтверждена.\nВремя: {_time(start)}"

def declined_text(tenant_name: str, start: datetime, reason: str) -> str:
    return f"❌ Ваша заявка на запись в «{tenant_name}» на {_time(start)} отклонена.\nПричина: {reason}"

def auto_cancelled_text(tenant_name: str, start: datetime) -> str:
    return (f"⌛ Ваша заявка на запись в «{tenant_name}» на {_time(start)} отменена автоматически: "
            f"организация не ответила вовремя.")

def notify_telegram_client(telegram_user_id: int, text: str) -> None:
    """
    Queues the message. Call only after the change it reports is committed. Never
    raises: the action is already done, and a broker outage must not turn it into
    an error for the staff member or the expiry job.
    """
    # Imported here: the task module pulls in the Celery app
    from src.core.celery.tasks.telegramClient_task import send_telegram_client_message
    try:
        send_telegram_client_message.delay(telegram_user_id, text)
    except Exception:
        logger.exception(f"Could not queue a message to Telegram user {telegram_user_id}")
