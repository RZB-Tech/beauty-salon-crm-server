"""
Click SHOP-API Prepare/Complete webhooks - Click calls these directly, so
they carry no session cookie and must stay on the open (unauthenticated)
router. Authenticity is verified per-request via the MD5 sign_string
instead (see src/core/utils/click.py), exactly as Click's protocol expects.
Responses must always be HTTP 200 with an `error` field - never an HTTP
error status - so these handlers never raise; failures are reported through
that field. That's also why every field defaults to "" instead of Form(...):
a missing field would otherwise be a FastAPI 422 that Click can't parse, so
it's left to the service to answer it with a Click error code instead.
"""
import logging

from fastapi import APIRouter, Depends, Form
from src.core.dependencies.uow import make_service_dependency
from src.services.payment.click_service import ClickPaymentService

logger = logging.getLogger(__name__)

router = APIRouter()

get_click_service = make_service_dependency(ClickPaymentService)

@router.post(
    "/prepare",
    summary = "Click SHOP-API: (Prepare)",
    description = "Регистрируется в личном кабинете Click как Prepare URL. Не вызывается напрямую."
)
async def click_prepare(
    click_trans_id: str = Form(""),
    service_id: str = Form(""),
    click_paydoc_id: str = Form(""),
    merchant_trans_id: str = Form(""),
    amount: str = Form(""),
    action: str = Form(""),
    sign_time: str = Form(""),
    sign_string: str = Form(""),
    error: str = Form("0"),
    error_note: str = Form(""),
    service: ClickPaymentService = Depends(get_click_service),
):
    result = await service.prepare(
        click_trans_id = click_trans_id,
        service_id = service_id,
        click_paydoc_id = click_paydoc_id,
        merchant_trans_id = merchant_trans_id,
        amount = amount,
        action = action,
        sign_time = sign_time,
        sign_string = sign_string,
    )
    if result["error"] != 0:
        logger.warning(
            "Click prepare rejected: error=%s (%s) click_trans_id=%r service_id=%r merchant_trans_id=%r amount=%r action=%r",
            result["error"], result["error_note"], click_trans_id, service_id, merchant_trans_id, amount, action,
        )
    return result

@router.post(
    "/complete",
    summary = "Click SHOP-API: (Complete)",
    description = "Регистрируется в личном кабинете Click как Complete URL. Не вызывается напрямую."
)
async def click_complete(
    click_trans_id: str = Form(""),
    service_id: str = Form(""),
    click_paydoc_id: str = Form(""),
    merchant_trans_id: str = Form(""),
    merchant_prepare_id: str = Form(""),
    amount: str = Form(""),
    action: str = Form(""),
    sign_time: str = Form(""),
    sign_string: str = Form(""),
    error: str = Form("0"),
    error_note: str = Form(""),
    service: ClickPaymentService = Depends(get_click_service),
):
    result = await service.complete(
        click_trans_id = click_trans_id,
        service_id = service_id,
        click_paydoc_id = click_paydoc_id,
        merchant_trans_id = merchant_trans_id,
        merchant_prepare_id = merchant_prepare_id,
        amount = amount,
        action = action,
        sign_time = sign_time,
        sign_string = sign_string,
        error = error,
        error_note = error_note,
    )
    if result["error"] != 0:
        logger.warning(
            "Click complete rejected: error=%s (%s) click_trans_id=%r merchant_trans_id=%r merchant_prepare_id=%r amount=%r click_error=%r click_error_note=%r",
            result["error"], result["error_note"], click_trans_id, merchant_trans_id, merchant_prepare_id, amount, error, error_note,
        )
    return result
