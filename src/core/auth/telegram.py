import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl

def validate_telegram_signed_data(raw: str, bot_token: str, max_age_seconds: int) -> dict[str, str]:
    """
    Validates a query string signed by Telegram with our bot token - WebApp initData,
    and also the response of WebApp.requestContact, which Telegram signs the same way.
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app

    Returns the parsed fields (hash removed); raises ValueError on any mismatch.
    """
    try:
        fields = dict(parse_qsl(raw, keep_blank_values = True, strict_parsing = True))
    except ValueError as e:
        raise ValueError("Malformed signed data") from e

    received_hash = fields.pop("hash", None)
    if not received_hash:
        raise ValueError("Signed data has no hash")

    # Only `hash` is excluded - `signature` (Ed25519, for third-party validation) stays in the check string
    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(fields.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(computed_hash, received_hash):
        raise ValueError("Signed data hash mismatch")

    try:
        auth_date = int(fields.get("auth_date", ""))
    except ValueError as e:
        raise ValueError("Signed data has no valid auth_date") from e
    if time.time() - auth_date > max_age_seconds:
        raise ValueError("Signed data expired")

    return fields

def parse_json_field(fields: dict[str, str], key: str) -> dict:
    try:
        value = json.loads(fields[key])
    except (KeyError, json.JSONDecodeError) as e:
        raise ValueError(f"Signed data has no valid '{key}'") from e
    if not isinstance(value, dict):
        raise ValueError(f"Signed data has no valid '{key}'")
    return value

def normalize_phone(phone: str) -> str:
    """Telegram sends contact phone numbers without '+' - store them as +<digits>."""
    digits = "".join(ch for ch in phone if ch.isdigit())
    return f"+{digits}"
