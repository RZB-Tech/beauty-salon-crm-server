from fastapi import APIRouter, Depends
from src.core.dependencies.permissions import require_permission
from src.core.dependencies.uow import make_service_dependency
from src.core.permissions import PermissionCode
from src.schemas.tenantSubscription.addon import (
    AddonProductResponseSchema,
    AddonPurchaseResponseSchema,
    AddonPurchaseSchema,
    TenantAddonResponseSchema,
)
from src.schemas.tenantSubscription.purchase import TenantSubscriptionPurchaseSchema
from src.schemas.tenantSubscription.response import TenantBillingStateSchema, TenantLimitsSchema, TenantSubscriptionResponseSchema
from src.services.system.tenantSubscription_service import TenantSubscriptionService

router = APIRouter()

get_tenantSubscription_service = make_service_dependency(TenantSubscriptionService)

@router.get(
    "",
    response_model = TenantBillingStateSchema,
    status_code = 200,
    summary = "Баланс и текущая подписка организации",
    description = "Доступно и без активной подписки, чтобы фронтенд мог показать баланс и предложить пополнить его или купить тариф.",
    dependencies = [Depends(require_permission([PermissionCode.SUBSCRIPTION_PAYMENT_READ]))]
)
async def get_current(service: TenantSubscriptionService = Depends(get_tenantSubscription_service)):
    return await service.get_current()

@router.get(
    "/limits",
    response_model = TenantLimitsSchema,
    status_code = 200,
    summary = "Лимиты тарифа и их использование",
    description = "Для каждого лимита (max_users, max_clients): сколько даёт тариф (plan), сколько добавили аддоны (addons), итоговый лимит (allowed), сколько занято (used) и сколько осталось (remaining). null в plan/allowed/remaining означает «без ограничений». Лимиты свои у каждой организации: у головной и у каждого филиала своя подписка, аддоны и лимиты. Архивные и неактивные сотрудники и клиенты тоже занимают место.",
    dependencies = [Depends(require_permission([PermissionCode.SUBSCRIPTION_PAYMENT_READ]))]
)
async def get_limits(service: TenantSubscriptionService = Depends(get_tenantSubscription_service)):
    return await service.get_limits()

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

@router.get(
    "/addon-products",
    response_model = list[AddonProductResponseSchema],
    status_code = 200,
    summary = "Каталог аддонов",
    description = "Аддоны, которые можно купить с баланса организации. Каждый увеличивает лимит limit_key на amount.",
    dependencies = [Depends(require_permission([PermissionCode.SUBSCRIPTION_PAYMENT_READ]))]
)
async def get_addon_products(service: TenantSubscriptionService = Depends(get_tenantSubscription_service)):
    return await service.get_addon_products()

@router.get(
    "/addons",
    response_model = list[TenantAddonResponseSchema],
    status_code = 200,
    summary = "Аддоны организации",
    description = "Купленные и выданные администратором аддоны организации. expires_at = null — бессрочный.",
    dependencies = [Depends(require_permission([PermissionCode.SUBSCRIPTION_PAYMENT_READ]))]
)
async def get_addons(service: TenantSubscriptionService = Depends(get_tenantSubscription_service)):
    return await service.get_addons()

@router.post(
    "/addons/purchase",
    response_model = AddonPurchaseResponseSchema,
    status_code = 200,
    summary = "Купить аддон с баланса организации",
    description = "Списывает цену аддона с баланса, создаёт расход (tenant_expenses, категория feature purchase) и бессрочно увеличивает лимит. Повторная покупка того же аддона суммируется.",
    dependencies = [Depends(require_permission([PermissionCode.SUBSCRIPTION_PAYMENT_PURCHASE]))]
)
async def purchase_addon(
    data: AddonPurchaseSchema,
    service: TenantSubscriptionService = Depends(get_tenantSubscription_service),
):
    return await service.purchase_addon(data)
