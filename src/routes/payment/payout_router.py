from fastapi import APIRouter, Depends, status
from src.core.dependencies.permissions import require_permission
from src.core.dependencies.uow import  make_service_dependency
from src.core.permissions import PermissionCode
from src.schemas.base import PaginatedResponseSchema, RequestAllObject
from src.schemas.payout.create import PayoutCreateSchema
from src.schemas.payout.response import PayoutResponseSchema
from src.services.payment.payout_service import PayoutService

router = APIRouter()

get_payout_service = make_service_dependency(PayoutService)

@router.post(
    "",
    response_model=PayoutResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary = "Провести выплату сотруднику",
    description = "Проводит выплату сотруднику. Для категории `other` можно указать либо конкретный список начислений (`payrolls`), либо период (`start_date`/`end_date`) — не оба сразу; будут выплачены все ожидающие премии/штрафы/комиссии за период. Для `salary`/`advance salary` начисления не указываются.",
    dependencies=[Depends(require_permission([PermissionCode.PAYOUT_CREATE]))]
)
async def create(data: PayoutCreateSchema,
                 payoutService: PayoutService = Depends(get_payout_service)):
    return await payoutService.create(data)

@router.post(
    "/get-all",
    response_model=PaginatedResponseSchema[PayoutResponseSchema],
    status_code=status.HTTP_200_OK,
    summary = "Получить все выплаты",
    description = "Возвращает постраничный список выплат сотрудникам с поддержкой фильтрации.",
    dependencies=[Depends(require_permission([PermissionCode.PAYOUT_READ]))]
)
async def get_all(params: RequestAllObject,
                 payoutService: PayoutService = Depends(get_payout_service)):
    return await payoutService.get_all(params)

@router.get(
    "/{id}",
    response_model=PayoutResponseSchema,
    status_code=status.HTTP_200_OK,
    summary = "Получить выплату по ID",
    dependencies=[Depends(require_permission([PermissionCode.PAYOUT_READ]))]
)
async def get(id: int,
                 payoutService: PayoutService = Depends(get_payout_service)):
    return await payoutService.get(id)