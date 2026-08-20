import traceback
from datetime import datetime, timezone
from functools import lru_cache
from html import escape

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from starlette.requests import Request

from src.core.config import settings
from src.core.dependencies.context import get_current_staff_id, get_current_tenant_id

MAX_MESSAGE_LENGTH = 4096
MAX_TRACEBACK_CHARS = 2000


@lru_cache(maxsize=1)
def _get_bot() -> Bot | None:
    if not settings.ERROR_ALERTS_BOT_TOKEN:
        return None
    return Bot(token=settings.ERROR_ALERTS_BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))


def _is_project_frame(frame: traceback.FrameSummary) -> bool:
    return "/site-packages/" not in frame.filename and "/.venv/" not in frame.filename


def _format_traceback(exc: Exception) -> str:
    """Only this app's own frames - library/framework internals (starlette,
    fastapi, sqlalchemy, ...) are noise for "what broke in our code"."""
    frames = traceback.extract_tb(exc.__traceback__)
    project_frames = [f for f in frames if _is_project_frame(f)] or frames

    tb = "".join(traceback.format_list(project_frames))
    tb += "".join(traceback.format_exception_only(type(exc), exc))
    return tb


def _format_message(request: Request, exc: Exception) -> str:
    tb = _format_traceback(exc)
    if len(tb) > MAX_TRACEBACK_CHARS:
        tb = tb[-MAX_TRACEBACK_CHARS:]

    lines = [
        "\U0001F6A8 <b>500 Internal Server Error</b>",
        f"<b>Time:</b> {datetime.now(timezone.utc).isoformat()}",
        f"<b>Request:</b> {escape(request.method)} {escape(request.url.path)}",
        f"<b>Tenant:</b> {get_current_tenant_id()}  <b>Staff:</b> {get_current_staff_id()}",
        f"<b>Exception:</b> {escape(type(exc).__name__)}: {escape(str(exc))}",
        f"<pre>{escape(tb)}</pre>",
    ]
    message = "\n".join(lines)
    return message[:MAX_MESSAGE_LENGTH]


async def send_error_alert(request: Request, exc: Exception) -> None:
    """
    Best-effort Telegram notification for unhandled (500) exceptions - never
    raises, so a broken/unset bot token can't turn a 500 response into a worse
    failure. No-ops silently if ERROR_ALERTS_BOT_TOKEN/ERROR_ALERTS_CHAT_ID
    aren't configured (see src/core/config.py), same "optional, degrade
    quietly" pattern this codebase already uses for Redis.
    """
    bot = _get_bot()
    if bot is None or not settings.ERROR_ALERTS_CHAT_ID:
        return

    try:
        await bot.send_message(chat_id=settings.ERROR_ALERTS_CHAT_ID, text=_format_message(request, exc))
    except Exception as send_exc:
        print(f"[telegram-alerts] failed to send error alert: {send_exc}")
