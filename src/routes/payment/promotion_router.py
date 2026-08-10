from fastapi import APIRouter, Depends
from src.core.dependencies.permissions import require_permission
from src.core.dependencies.uow import  make_service_dependency
from src.core.permissions import PermissionCode
from src.schemas.base import PaginatedResponseSchema, RequestAllObject
from src.schemas.promotion.create import PromotionCreateSchema
from src.schemas.promotion.response import PromotionResponseSchema
from src.schemas.promotion.update import PromotionUpdateSchema
from src.services.payment.promotion_service import PromotionService

router = APIRouter()

get_promotion_service = make_service_dependency(PromotionService)

@router.post(
    "",
    response_model=PromotionResponseSchema,
    status_code= 201,
    summary = "Создать акцию",
    description = "Создает акцию (`percentage`, `fixed_amount` или `bogo`). В `conditions` для `percentage`/`fixed_amount` указываются `services` и/или `materials`, на которые распространяется скидка, а для `bogo` — пара `buy`/`get`.",
    dependencies=[Depends(require_permission([PermissionCode.PROMOTION_CREATE]))]
)
async def create(data: PromotionCreateSchema,
                 promotionService: PromotionService = Depends(get_promotion_service)):
    return await promotionService.create(data)

@router.patch(
    "",
    response_model=PromotionResponseSchema,
    status_code= 200,
    summary = "Обновить акцию",
    description = "Обновляет акцию по её `id`. Нельзя обновить архивированную акцию; тип акции (`promo_type`) должен оставаться согласован с условиями (`conditions`).",
    dependencies=[Depends(require_permission([PermissionCode.PROMOTION_UPDATE]))]
)
async def update(data: PromotionUpdateSchema,
                 promotionService: PromotionService = Depends(get_promotion_service)):
    return await promotionService.update(data)

@router.post(
    "/get-all",
    response_model=PaginatedResponseSchema[PromotionResponseSchema],
    status_code = 200,
    summary = "Получить все акции",
    description = "Возвращает постраничный список акций с поддержкой фильтрации.",
    dependencies=[Depends(require_permission([PermissionCode.PROMOTION_GET]))]
)
async def get_all(params: RequestAllObject,
                 promotionService: PromotionService = Depends(get_promotion_service)):
    return await promotionService.get_all(params)

@router.get(
    "/{id}",
    response_model = PromotionResponseSchema,
    status_code = 200,
    summary = "Получить акцию по ID",
    dependencies=[Depends(require_permission([PermissionCode.PROMOTION_GET]))]
)
async def get(id: int,
                promotionService: PromotionService = Depends(get_promotion_service)):
    return await promotionService.get(id)