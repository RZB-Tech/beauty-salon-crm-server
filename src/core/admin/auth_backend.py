from sqlalchemy import select
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from src.core.admin.security import create_admin_access_token, decode_admin_access_token
from src.core.auth.security import verify_password
from src.database.session import SessionLocal
from src.repository.platform.platformUser_model import PlatformUser

class AdminAuthBackend(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        login = str(form.get("username") or "").strip().lower()
        password = str(form.get("password") or "")

        if not login or not password:
            return False

        async with SessionLocal() as session:
            result = await session.execute(
                select(PlatformUser).where(PlatformUser.login == login)
            )
            user = result.scalar_one_or_none()

        if user is None or not verify_password(user.hashed_password, password):
            return False

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
