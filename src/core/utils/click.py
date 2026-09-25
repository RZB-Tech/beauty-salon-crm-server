"""
Click SHOP-API signature handling for the Prepare/Complete webhooks Click
sends to us (MD5, built from the exact form fields Click sent, as strings,
concatenated in order). Signature mismatches are almost always caused by
re-formatting numbers (e.g. "1000" vs "1000.00") before hashing - always
hash the raw string values exactly as received.
"""
import hashlib

from src.core.config import settings

# Standard Click SHOP-API error codes; merchant response bodies must always
# be HTTP 200 with one of these in the `error` field, never an HTTP error.
CLICK_ERROR_SUCCESS = 0
CLICK_ERROR_SIGN_FAILED = -1
CLICK_ERROR_AMOUNT = -2
CLICK_ERROR_ACTION_NOT_FOUND = -3
CLICK_ERROR_ALREADY_PAID = -4
CLICK_ERROR_ORDER_NOT_FOUND = -5
CLICK_ERROR_TRANSACTION_NOT_FOUND = -6
CLICK_ERROR_FAILED_TO_UPDATE = -7
CLICK_ERROR_BAD_REQUEST = -8
CLICK_ERROR_TRANSACTION_CANCELLED = -9

# Click sends `action` as a form string: "0" on Prepare, "1" on Complete.
CLICK_ACTION_PREPARE = "0"
CLICK_ACTION_COMPLETE = "1"


def make_prepare_sign(click_trans_id: str, service_id: str, merchant_trans_id: str,
                       amount: str, action: str, sign_time: str) -> str:
    raw = f"{click_trans_id}{service_id}{settings.CLICK_SECRET_KEY}{merchant_trans_id}{amount}{action}{sign_time}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def make_complete_sign(click_trans_id: str, service_id: str, merchant_trans_id: str,
                        merchant_prepare_id: str, amount: str, action: str, sign_time: str) -> str:
    raw = (
        f"{click_trans_id}{service_id}{settings.CLICK_SECRET_KEY}{merchant_trans_id}"
        f"{merchant_prepare_id}{amount}{action}{sign_time}"
    )
    return hashlib.md5(raw.encode("utf-8")).hexdigest()
