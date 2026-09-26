from fastapi import Depends, Header
from src.core.auth.telegram import parse_json_field, validate_telegram_signed_data
from src.core.config import settings
from src.core.dependencies.uow import UnitOfWork, get_request_uow
from src.exceptions.appointmentRequest_exceptions import GlobalClientNotRegistered
from src.exceptions.auth_exceptions import TelegramAuthInvalid, TelegramMiniAppNotConfigured
from src.repository.globalClient.globalClient_model import GlobalClient

async def get_telegram_user(authorization: str | None = Header(None)) -> dict:
    """
    Telegram mini app auth: `Authorization: tma <initData>`, validated against our
    bot token on every request (stateless - no session/JWT for mini app clients).
    """
    if not settings.TELEGRAM_MINIAPP_BOT_TOKEN: raise TelegramMiniAppNotConfigured()

    scheme, _, init_data = (authorization or "").partition(" ")
    if scheme.lower() != "tma" or not init_data: raise TelegramAuthInvalid()

    try:
        fields = validate_telegram_signed_data(
            init_data, settings.TELEGRAM_MINIAPP_BOT_TOKEN, settings.TELEGRAM_INIT_DATA_EXPIRE_SECONDS)
        user = parse_json_field(fields, "user")
    except ValueError:
        raise TelegramAuthInvalid()

    if not isinstance(user.get("id"), int): raise TelegramAuthInvalid()
    return user

async def get_current_global_client(
    user: dict = Depends(get_telegram_user),
    uow: UnitOfWork = Depends(get_request_uow)
) -> GlobalClient:
    """
    Registered global client of the Telegram user. Everything in the mini app
    except registration needs one - not registered yet -> GLOBAL_CLIENT_NOT_REGISTERED,
    and the mini app shows the registration form (POST /mini-app/me).
    """
    client = await uow.globalClients.get_by_telegram_user_id(user["id"])
    if client is None: raise GlobalClientNotRegistered()
    return client
