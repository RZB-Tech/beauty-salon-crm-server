from fastapi import APIRouter, Depends
from src.core.dependencies.permissions import require_permission
from src.core.dependencies.uow import  make_service_dependency
from src.core.permissions import PermissionCode
from src.schemas.base import PaginatedResponseSchema, RequestAllObject
from src.schemas.giftCard.create import GiftCardCreateSchema
from src.schemas.giftCard.request import GiftCardCancelSchema
from src.schemas.giftCard.response import GiftCardResponseSchema
from src.schemas.giftCard.update import GiftCardUpdateSchema
from src.services.payment.giftCard_service import GiftCardService

router = APIRouter()

get_giftCard_service = make_service_dependency(GiftCardService)

@router.post(
    "",
    response_model=GiftCardResponseSchema,
    status_code = 201,
    summary = "Создать подарочный сертификат",
    description = "Создает подарчный купон: `client_id` является опциональным",
    dependencies=[Depends(require_permission([PermissionCode.GIFT_CARD_CREATE]))]
)
async def create(data: GiftCardCreateSchema,
                 giftCardService: GiftCardService = Depends(get_giftCard_service)):
    return await giftCardService.create(data)

@router.patch(
    "",
    response_model=GiftCardResponseSchema,
    status_code= 200,
    summary = "Обновить подарочный купон",
    description = "Обновляет подарочный купон по её `id`. Можно указать опциональное поле `client_id`, если указывается, то созданные купон может быть использован только этим клиентом. Нельзя обновить архивированную акцию",
    dependencies=[Depends(require_permission([PermissionCode.GIFT_CARD_UPDATE]))]
)
async def update(data: GiftCardUpdateSchema,
                 giftCardService: GiftCardService = Depends(get_giftCard_service)):
    return await giftCardService.update(data)

@router.post(
    "/get-all",
    response_model=PaginatedResponseSchema[GiftCardResponseSchema],
    status_code = 200,
    summary = "Получить все подарчные купоны",
    description = "Возвращает постраничный список подарочных купонов с поддержкой фильтрации.",
    dependencies=[Depends(require_permission([PermissionCode.GIFT_CARD_GET]))]
)
async def update(params: RequestAllObject,
                 giftCardService: GiftCardService = Depends(get_giftCard_service)):
    return await giftCardService.get_all(params)

@router.get(
    "/{id}",
    response_model=GiftCardResponseSchema,
    status_code = 200,
    summary = "Получить подарчный купон по ID",
    dependencies=[Depends(require_permission([PermissionCode.GIFT_CARD_GET]))]
)
async def get(id: int,
                 giftCardService: GiftCardService = Depends(get_giftCard_service)):
    return await giftCardService.get(id)

@router.post(
    "/cancel",
    response_model = GiftCardResponseSchema,
    status_code = 200,
    summary = "Отменить подарочный купон. Можно отменить только не использованный купон (если остаток == `initial_amount`)",
    dependencies = [Depends(require_permission([PermissionCode.GIFT_CARD_UPDATE]))]
)
async def cancel(data: GiftCardCancelSchema,
                 giftCardService: GiftCardService = Depends(get_giftCard_service)):
    return await giftCardService.cancel(data)