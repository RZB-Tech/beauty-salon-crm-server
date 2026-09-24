from fastapi import APIRouter, Depends
from src.core.dependencies.permissions import require_permission
from src.core.dependencies.uow import make_service_dependency
from src.core.permissions import PermissionCode
from src.schemas.tenantSubscription.purchase import TenantSubscriptionPurchaseSchema
from src.schemas.tenantSubscription.response import TenantSubscriptionResponseSchema
from src.services.system.tenantSubscription_service import TenantSubscriptionService

router = APIRouter()

get_tenantSubscription_service = make_service_dependency(TenantSubscriptionService)

@router.post(
    "/purchase",
    response_model = TenantSubscriptionResponseSchema,
    status_code = 200,
    summary = "Купить/продлить тарифный план из баланса организации",
    description = "Списывает стоимость выбранного тарифа с баланса организации, создаёт расход (tenant_expenses) и активирует подписку. Требует баланс не меньше стоимости тарифа.",
    dependencies = [Depends(require_permission([PermissionCode.SUBSCRIPTION_PAYMENT_PURCHASE]))]
)
async def purchase(
    data: TenantSubscriptionPurchaseSchema,
    service: TenantSubscriptionService = Depends(get_tenantSubscription_service),
):
    return await service.purchase(data)
