from fastapi import APIRouter, Depends
from src.core.dependencies.auth import get_current_staff
from src.core.dependencies.permissions import require_permission
from src.core.dependencies.uow import make_service_dependency
from src.core.permissions import PermissionCode
from src.schemas.clickPayment.create import ClickCheckoutCreateSchema
from src.schemas.clickPayment.response import ClickCheckoutResponseSchema, ClickPaymentStatusSchema
from src.services.payment.click_service import ClickPaymentService

router = APIRouter()

get_click_service = make_service_dependency(ClickPaymentService)

@router.post(
    "/checkout",
    response_model = ClickCheckoutResponseSchema,
    status_code = 201,
    summary = "Создать ссылку пополнения баланса через Click",
    description = "Создаёт платёж на указанную сумму для организации текущего сотрудника и возвращает ссылку на оплату Click. Сумма зачисляется на баланс организации (см. /tenant-subscription/purchase для траты баланса на тариф).",
    dependencies = [Depends(require_permission([PermissionCode.SUBSCRIPTION_PAYMENT_CREATE]))]
)
async def create_checkout(
    data: ClickCheckoutCreateSchema,
    service: ClickPaymentService = Depends(get_click_service),
):
    return await service.create_checkout(data)

@router.get(
    "/{payment_id}",
    response_model = ClickPaymentStatusSchema,
    status_code = 200,
    summary = "Статус платежа Click",
    description = "Для страницы CLICK_RETURN_URL: сам редирект браузера не подтверждает оплату, поэтому фронтенд опрашивает этот эндпоинт, пока статус не станет completed или cancelled.",
    dependencies = [Depends(require_permission([PermissionCode.SUBSCRIPTION_PAYMENT_READ]))]
)
async def get_payment_status(
    payment_id: int,
    service: ClickPaymentService = Depends(get_click_service),
):
    return await service.get_payment_status(payment_id)
