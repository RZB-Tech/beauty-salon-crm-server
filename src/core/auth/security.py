from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError
from datetime import datetime, timedelta, timezone
import jwt
from src.core.config import settings

ph = PasswordHasher()

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(hashed_password: str, password: str) -> bool:
    try:
        return ph.verify(hashed_password, password)
    except VerifyMismatchError:
        return False
    except VerificationError:
        return False
    
def create_access_token(data: dict) -> str:
    toEncode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(seconds = settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    toEncode.update({"exp": expire})
    return jwt.encode(toEncode, settings.PRIVATE_KEY, algorithm = settings.ALGORITHM)

def create_refresh_token(data: dict) -> str:
    toEncode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(seconds = settings.REFRESH_TOKEN_EXPIRE_SECONDS)
    toEncode.update({"exp": expire})
    return jwt.encode(toEncode, settings.PRIVATE_KEY, algorithm = settings.ALGORITHM)

def decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.PUBLIC_KEY, algorithms = [settings.ALGORITHM])
        return payload
    except jwt.PyJWTError: 
        return None