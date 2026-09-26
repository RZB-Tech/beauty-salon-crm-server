import asyncio
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from src.core.celery.celeryApp import celery_app
from src.core.config import settings

logger = logging.getLogger(__name__)

@celery_app.task(name = "send_telegram_client_message")
def send_telegram_client_message(telegram_user_id: int, text: str):
    asyncio.run(_send(telegram_user_id, text))

async def _send(telegram_user_id: int, text: str) -> None:
    """
    Message from the mini app's bot to a client. Best-effort: Telegram refuses it
    if the client never started the bot or blocked it (the mini app should ask for
    write access, WebApp.requestWriteAccess) - nothing to retry then, just log.
    Plain text, no parse mode, so tenant names can't break the message.
    """
    if not settings.TELEGRAM_MINIAPP_BOT_TOKEN:
        return
    async with Bot(token = settings.TELEGRAM_MINIAPP_BOT_TOKEN) as bot:
        try:
            await bot.send_message(telegram_user_id, text)
        except TelegramAPIError as e:
            logger.warning(f"Could not message Telegram user {telegram_user_id}: {e}")
