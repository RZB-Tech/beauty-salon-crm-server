from fastapi import APIRouter, Depends, status
from src.core.dependencies.permissions import require_permission
from src.core.dependencies.uow import make_service_dependency
from src.core.permissions import PermissionCode
from src.schemas.base import PaginatedResponseSchema, RequestAllObject
from src.schemas.transaction.create import TransactionCreateSchema
from src.schemas.transaction.response import TransactionResponseSchema
from src.services.payment.transaction_service import TransactionService

router = APIRouter()
get_transaction_service = make_service_dependency(TransactionService)

@router.post(
    "",
    response_model=TransactionResponseSchema,
    status_code = 201,
    summary="Создать новую транзакцию",
    description="Создает ручную транзакцию дохода/расхода (например, оплата коммунальных услуг). Транзакции с категорией `receipt` или `employee payment` создавать вручную нельзя — система генерирует их автоматически при оплате чеков и выплатах сотрудникам.",
    dependencies=[Depends(require_permission([PermissionCode.TRANSACTION_CREATE]))]
)
async def create(data: TransactionCreateSchema,
                 transactionService: TransactionService = Depends(get_transaction_service)):
    return await transactionService.create(data)

@router.post(
    "/get-all",
    response_model=PaginatedResponseSchema[TransactionResponseSchema],
    status_code = 200,
    summary="Получить все транзакции",
    description="Возвращает постраничный список транзакций организации с поддержкой фильтрации.",
    dependencies=[Depends(require_permission([PermissionCode.TRANSACTION_READ]))]
)
async def get_all(params: RequestAllObject,
                 transactionService: TransactionService = Depends(get_transaction_service)):
    return await transactionService.get_all(params)


@router.get(
    "/{id}",
    response_model=TransactionResponseSchema,
    status_code = 200,
    summary="Получить транзакцию по ID",
    description="Возвращает транзакцию по её `id`.",
    dependencies=[Depends(require_permission([PermissionCode.TRANSACTION_READ]))]
)
async def get(id: int,
                 transactionService: TransactionService = Depends(get_transaction_service)):
    return await transactionService.get(id)

@router.post(
    "/{id}/cancel",
    response_model = TransactionResponseSchema,
    status_code = 200,
    summary = "Отменить транзакцию",
    description = "Отменяет ручную транзакцию по её `id`. Автоматически сгенерированные транзакции (связанные с чеками или выплатами) отменить нельзя — нужно отменить связанный чек или выплату.",
    dependencies=[Depends(require_permission([PermissionCode.TRANSACTION_CANCEL]))]
)
async def cancel(id: int,
                 transactionService: TransactionService = Depends(get_transaction_service)):
    return await transactionService.cancel(id)