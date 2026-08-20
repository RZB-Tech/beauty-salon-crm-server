from datetime import datetime, timezone
import re

def as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)

def validate_contain_only_alpha_and_digits(value: str) -> bool:
    return False if re.fullmatch(r"[a-zA-Z0-9]+", value) is None else True