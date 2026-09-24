from decimal import Decimal, InvalidOperation
from urllib.parse import urlencode

from src.core.config import settings
from src.core.dependencies.context import get_current_tenant_id
from src.core.dependencies.uow import UnitOfWork
from src.core.utils.click import (
    CLICK_ERROR_ALREADY_PAID,
    CLICK_ERROR_AMOUNT,
    CLICK_ERROR_BAD_REQUEST,
    CLICK_ERROR_ORDER_NOT_FOUND,
    CLICK_ERROR_SIGN_FAILED,
    CLICK_ERROR_SUCCESS,
    CLICK_ERROR_TRANSACTION_CANCELLED,
    CLICK_ERROR_TRANSACTION_NOT_FOUND,
    make_complete_sign,
    make_prepare_sign,
)
from src.exceptions.auth_exceptions import AuthTenantContextEmpty
from src.exceptions.tenant_exceptions import TenantNotFound
from src.repository.tenant.payments.tenantPayments_model import TenantPayments, TenantPaymentStatus
from src.schemas.clickPayment.create import ClickCheckoutCreateSchema
from src.schemas.clickPayment.response import ClickCheckoutResponseSchema

GATEWAY = "Click"

def _safe_int(value: str) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


class ClickPaymentService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create_checkout(self, data: ClickCheckoutCreateSchema) -> ClickCheckoutResponseSchema:
        tenantID = get_current_tenant_id()
        if tenantID is None: raise AuthTenantContextEmpty()

        tenant = await self.uow.tenants.get(id = tenantID)
        if tenant is None: raise TenantNotFound(tenantID)

        payment = await self.uow.tenantPayments.create(TenantPayments(
            tenant_id = tenant.id,
            tenant_snapshot = {"id": tenant.id, "name": tenant.name, "TIN": tenant.TIN},
            amount = data.amount,
            status = TenantPaymentStatus.PENDING,
            gateway = GATEWAY,
        ))

        checkout_url = settings.CLICK_CHECKOUT_URL + "?" + urlencode({
            "service_id": settings.CLICK_SERVICE_ID,
            "merchant_id": settings.CLICK_MERCHANT_ID,
            "amount": str(payment.amount),
            "transaction_param": payment.id,
            "return_url": settings.CLICK_RETURN_URL,
        })

        return ClickCheckoutResponseSchema(
            transaction_id = payment.id,
            checkout_url = checkout_url,
            amount = payment.amount,
        )

    async def prepare(
        self,
        click_trans_id: str,
        service_id: str,
        click_paydoc_id: str,
        merchant_trans_id: str,
        amount: str,
        action: str,
        sign_time: str,
        sign_string: str,
    ) -> dict:
        def resp(merchant_prepare_id, error: int, error_note: str) -> dict:
            return {
                "click_trans_id": click_trans_id,
                "merchant_trans_id": merchant_trans_id,
                "merchant_prepare_id": merchant_prepare_id,
                "error": error,
                "error_note": error_note,
            }

        expected_sign = make_prepare_sign(click_trans_id, service_id, merchant_trans_id, amount, action, sign_time)
        if expected_sign != sign_string:
            return resp(0, CLICK_ERROR_SIGN_FAILED, "SIGN CHECK FAILED!")

        if _safe_int(service_id) != settings.CLICK_SERVICE_ID:
            return resp(0, CLICK_ERROR_BAD_REQUEST, "Wrong service_id")

        payment_id = _safe_int(merchant_trans_id)
        if payment_id is None:
            return resp(0, CLICK_ERROR_ORDER_NOT_FOUND, "Order not found")

        payment = await self.uow.tenantPayments.get(payment_id, lock = True)
        if payment is None or payment.gateway != GATEWAY:
            return resp(0, CLICK_ERROR_ORDER_NOT_FOUND, "Order not found")

        try:
            if Decimal(amount) != payment.amount:
                return resp(0, CLICK_ERROR_AMOUNT, "Incorrect amount")
        except InvalidOperation:
            return resp(0, CLICK_ERROR_AMOUNT, "Incorrect amount")

        incoming_click_trans_id = _safe_int(click_trans_id)

        if payment.status == TenantPaymentStatus.COMPLETED:
            return resp(payment.id, CLICK_ERROR_ALREADY_PAID, "Already paid")

        if payment.status == TenantPaymentStatus.CANCELLED:
            return resp(payment.id, CLICK_ERROR_TRANSACTION_CANCELLED, "Transaction cancelled")

        if payment.status == TenantPaymentStatus.PROCESSING:
            if payment.gateway_transaction_id == str(incoming_click_trans_id):
                return resp(payment.id, CLICK_ERROR_SUCCESS, "Success")
            return resp(0, CLICK_ERROR_TRANSACTION_NOT_FOUND, "Transaction not found")

        payment.gateway_transaction_id = str(incoming_click_trans_id)
        payment.gateway_metadata = {**payment.gateway_metadata, "click_paydoc_id": _safe_int(click_paydoc_id)}
        payment.status = TenantPaymentStatus.PROCESSING

        return resp(payment.id, CLICK_ERROR_SUCCESS, "Success")

    async def complete(
        self,
        click_trans_id: str,
        service_id: str,
        click_paydoc_id: str,
        merchant_trans_id: str,
        merchant_prepare_id: str,
        amount: str,
        action: str,
        sign_time: str,
        sign_string: str,
        error: str,
        error_note: str,
    ) -> dict:
        def resp(merchant_confirm_id, error_code: int, note: str) -> dict:
            return {
                "click_trans_id": click_trans_id,
                "merchant_trans_id": merchant_trans_id,
                "merchant_confirm_id": merchant_confirm_id,
                "error": error_code,
                "error_note": note,
            }

        expected_sign = make_complete_sign(
            click_trans_id, service_id, merchant_trans_id, merchant_prepare_id, amount, action, sign_time
        )
        if expected_sign != sign_string:
            return resp(None, CLICK_ERROR_SIGN_FAILED, "SIGN CHECK FAILED!")

        payment = await self.uow.tenantPayments.get_by_gateway_transaction(GATEWAY, click_trans_id, lock = True)
        if payment is None or payment.id != _safe_int(merchant_prepare_id):
            return resp(None, CLICK_ERROR_TRANSACTION_NOT_FOUND, "Transaction not found")

        if payment.status == TenantPaymentStatus.COMPLETED:
            return resp(payment.id, CLICK_ERROR_ALREADY_PAID, "Already paid")

        if payment.tenant_id is None:
            return resp(payment.id, CLICK_ERROR_ORDER_NOT_FOUND, "Order not found")

        error_code = _safe_int(error)
        if error_code is not None and error_code < 0:
            payment.status = TenantPaymentStatus.CANCELLED
            return resp(payment.id, CLICK_ERROR_TRANSACTION_CANCELLED, "Transaction cancelled")

        tenant = await self.uow.tenants.get(id = payment.tenant_id, lock = True)
        if tenant is None:
            return resp(payment.id, CLICK_ERROR_ORDER_NOT_FOUND, "Order not found")

        tenant.balance = tenant.balance + payment.amount
        payment.status = TenantPaymentStatus.COMPLETED

        return resp(payment.id, CLICK_ERROR_SUCCESS, "Success")
