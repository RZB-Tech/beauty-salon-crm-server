import logging

from sqlalchemy import select
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from src.core.admin.security import create_admin_access_token, decode_admin_access_token
from src.core.auth.security import verify_password
from src.core.cache.admin_login_cache import is_admin_login_blocked, register_failed_admin_login, reset_failed_admin_login
from src.core.utils.common import get_client_ip
from src.database.session import SessionLocal
from src.repository.platform.platformUser_model import PlatformUser

logger = logging.getLogger(__name__)

class AdminAuthBackend(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        login = str(form.get("username") or "").strip().lower()
        password = str(form.get("password") or "")

        if not login or not password:
            return False

        ip = get_client_ip(request)

        # Checked before the password: a blocked login or IP gets no more
        # guesses, even correct ones. SQLAdmin shows its generic "Invalid
        # credentials." either way, so the block isn't revealed to the client.
        if await is_admin_login_blocked(ip, login):
            logger.warning("Blocked SQLAdmin login attempt: login=%s ip=%s", login, ip)
            return False

        async with SessionLocal() as session:
            result = await session.execute(
                select(PlatformUser).where(PlatformUser.login == login)
            )
            user = result.scalar_one_or_none()

            # Unknown and deactivated logins count as failures too, same as a
            # wrong password - otherwise they'd be free guesses for the IP.
            if user is None or not user.active or not verify_password(user.hashed_password, password):
                await register_failed_admin_login(ip, login)
                return False

            await reset_failed_admin_login(ip, login)
            token = create_admin_access_token({"sub": user.login, "id": user.id})

        request.session.update({"token": token})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        if not token:
            return False

        payload = decode_admin_access_token(token)
        return payload is not None and payload.get("type") == "admin_access"
