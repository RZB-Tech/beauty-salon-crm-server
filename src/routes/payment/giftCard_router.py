from fastapi import APIRouter, Depends
from src.core.dependencies.permissions import require_permission
from src.core.dependencies.uow import  make_service_dependency
from src.core.permissions import PermissionCode
from src.schemas.base import PaginatedResponseSchema, RequestAllObject
from src.schemas.giftCard.create import GiftCardCreateSchema
from src.schemas.giftCard.response import GiftCardResponseSchema
from src.services.payment.giftCard_service import GiftCardService

router = APIRouter()

get_giftCard_service = make_service_dependency(GiftCardService)

@router.post(
    "",
    response_model=GiftCardResponseSchema,
    status_code = 201,
    summary = "Создать подарочный сертификат",
    description = "Создает подарчный купон: `client_id` является опциональным",
    dependencies=[Depends(require_permission([PermissionCode.PAYROLL_CREATE]))]
)
async def create(data: GiftCardCreateSchema,
                 giftCardService: GiftCardService = Depends(get_giftCard_service)):
    return await giftCardService.create(data)