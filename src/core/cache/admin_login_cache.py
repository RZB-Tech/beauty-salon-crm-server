"""
Failed SQLAdmin login tracking - same mechanism as the staff login
(login_attempts_cache), with its own keys and stricter limits from settings:
a login is blocked after ADMIN_LOGIN_MAX_FAILED_ATTEMPTS from any IP, an IP
after ADMIN_IP_MAX_FAILED_ATTEMPTS across any logins. Blocks expire on their own.
If Redis is down, nothing is counted or blocked (same as the staff login).
"""
from src.core.cache.login_attempts_cache import _is_blocked, _register_failure, _reset
from src.core.config import settings

def _ip_attempts_key(ip: str) -> str:
    return f"admin_login_ip:{ip}:attempts"

def _ip_blocked_key(ip: str) -> str:
    return f"admin_login_ip:{ip}:blocked"

def _account_attempts_key(login: str) -> str:
    return f"admin_login_account:{login}:attempts"

def _account_blocked_key(login: str) -> str:
    return f"admin_login_account:{login}:blocked"

async def is_admin_login_blocked(ip: str, login: str) -> bool:
    return await _is_blocked(_ip_blocked_key(ip)) or await _is_blocked(_account_blocked_key(login))

async def register_failed_admin_login(ip: str, login: str) -> None:
    await _register_failure(
        _ip_attempts_key(ip), _ip_blocked_key(ip), "admin ip", ip,
        settings.ADMIN_IP_MAX_FAILED_ATTEMPTS, settings.ADMIN_ATTEMPTS_WINDOW_TTL, settings.ADMIN_IP_BLOCK_TTL,
    )
    await _register_failure(
        _account_attempts_key(login), _account_blocked_key(login), "admin login", login,
        settings.ADMIN_LOGIN_MAX_FAILED_ATTEMPTS, settings.ADMIN_ATTEMPTS_WINDOW_TTL, settings.ADMIN_LOGIN_BLOCK_TTL,
    )

async def reset_failed_admin_login(ip: str, login: str) -> None:
    await _reset(_ip_attempts_key(ip), _ip_blocked_key(ip))
    await _reset(_account_attempts_key(login), _account_blocked_key(login))
