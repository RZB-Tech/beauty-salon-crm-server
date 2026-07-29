from datetime import datetime, timedelta, timezone
import jwt
from src.core.config import settings

def create_admin_access_token(data: dict) -> str:
    toEncode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(seconds = settings.ADMIN_ACCESS_TOKEN_EXPIRE_SECONDS)
    toEncode.update({"exp": expire, "type": "admin_access"})
    return jwt.encode(toEncode, settings.ADMIN_PRIVATE_KEY, algorithm = settings.ADMIN_ALGORITHM)

def decode_admin_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.ADMIN_PUBLIC_KEY, algorithms = [settings.ADMIN_ALGORITHM])
    except jwt.PyJWTError:
        return None
