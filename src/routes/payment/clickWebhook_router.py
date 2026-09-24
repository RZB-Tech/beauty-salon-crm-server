"""
Click SHOP-API Prepare/Complete webhooks - Click calls these directly, so
they carry no session cookie and must stay on the open (unauthenticated)
router. Authenticity is verified per-request via the MD5 sign_string
instead (see src/core/utils/click.py), exactly as Click's protocol expects.
Responses must always be HTTP 200 with an `error` field - never an HTTP
error status - so these handlers never raise; failures are reported through
that field.
"""
from fastapi import APIRouter, Depends, Form
from src.core.dependencies.uow import make_service_dependency
from src.services.payment.click_service import ClickPaymentService

router = APIRouter()

get_click_service = make_service_dependency(ClickPaymentService)

@router.post(
    "/prepare",
    summary = "Click SHOP-API: (Prepare)",
    description = "Регистрируется в личном кабинете Click как Prepare URL. Не вызывается напрямую."
)
async def click_prepare(
    click_trans_id: str = Form(...),
    service_id: str = Form(...),
    click_paydoc_id: str = Form(...),
    merchant_trans_id: str = Form(...),
    amount: str = Form(...),
    action: str = Form(...),
    sign_time: str = Form(...),
    sign_string: str = Form(...),
    error: str = Form("0"),
    error_note: str = Form(""),
    service: ClickPaymentService = Depends(get_click_service),
):
    return await service.prepare(
        click_trans_id = click_trans_id,
        service_id = service_id,
        click_paydoc_id = click_paydoc_id,
        merchant_trans_id = merchant_trans_id,
        amount = amount,
        action = action,
        sign_time = sign_time,
        sign_string = sign_string,
    )

@router.post(
    "/complete",
    summary = "Click SHOP-API: (Complete)",
    description = "Регистрируется в личном кабинете Click как Complete URL. Не вызывается напрямую."
)
async def click_complete(
    click_trans_id: str = Form(...),
    service_id: str = Form(...),
    click_paydoc_id: str = Form(...),
    merchant_trans_id: str = Form(...),
    merchant_prepare_id: str = Form(...),
    amount: str = Form(...),
    action: str = Form(...),
    sign_time: str = Form(...),
    sign_string: str = Form(...),
    error: str = Form("0"),
    error_note: str = Form(""),
    service: ClickPaymentService = Depends(get_click_service),
):
    return await service.complete(
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
