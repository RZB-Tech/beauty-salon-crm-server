from fastapi import APIRouter, Depends, status
from src.core.dependencies.permissions import require_permission
from src.core.dependencies.uow import  make_service_dependency
from src.schemas.subscriptionPlan.response import SubscriptionPlanResponseSchema
from src.services.system.subscriptionPlans_service import SubscriptionPlanService

router = APIRouter()

get_subscriptionPlan_service = make_service_dependency(SubscriptionPlanService)

@router.get(
    "/get-all",
    response_model = list[SubscriptionPlanResponseSchema],
    status_code = 200,
    summary = "Получить все подписки"
)
async def get_all(service: SubscriptionPlanService = Depends(get_subscriptionPlan_service)):
    return await service.get_all()

@router.get(
    "/{id}",
    response_model=SubscriptionPlanResponseSchema,
    status_code = 200,
    summary = "Получить конкретную подписку"
)
async def get(id: int, service: SubscriptionPlanService = Depends(get_subscriptionPlan_service)):
    return await service.get(id)