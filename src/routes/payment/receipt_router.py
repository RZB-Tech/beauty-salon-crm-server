from fastapi import APIRouter, Depends, status
from src.core.dependencies.permissions import require_permission
from src.core.dependencies.uow import UnitOfWork, get_uow_with_context, make_service_dependency
from src.core.permissions import PermissionCode
from src.schemas.base import PaginatedResponseSchema, RequestAllObject
from src.schemas.payment.create import ReceiptCreateSchema, ReceiptPaymentCreateSchema
from src.schemas.payment.response import ReceiptResponseSchema
from src.services.payment.receipt_service import ReceiptService

router = APIRouter()

get_receipt_service = make_service_dependency(ReceiptService)

@router.post(
    "",
    response_model=ReceiptResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary = "Создать чек",
    description = "Создает чек по посещению (`receipt_type: appointment` + `appointment_id`, сумма считается по услугам/товарам из записей посещения) либо чек прямой продажи (`receipt_type: direct sale` + `client_id` и список `receipt_items`, списывает товары со склада).",
    dependencies=[Depends(require_permission([PermissionCode.RECEIPT_CREATE]))]
)
async def create(data: ReceiptCreateSchema,
                 receiptService: ReceiptService = Depends(get_receipt_service)):
    return await receiptService.create(data)

@router.get(
    "/{id}",
    response_model = ReceiptResponseSchema,
    status_code = 200,
    summary = "Получить чек по ID",
    dependencies=[Depends(require_permission([PermissionCode.RECEIPT_READ]))]
)
async def get(id: int,
              receiptService: ReceiptService = Depends(get_receipt_service)):
    return await receiptService.get(id)

@router.post(
    "/get-all",
    response_model=PaginatedResponseSchema[ReceiptResponseSchema],
    status_code= 200,
    summary="Получить все чеки",
    description="Возвращает постраничный список чеков организации с поддержкой фильтрации.",
    dependencies=[Depends(require_permission([PermissionCode.RECEIPT_READ]))]
)
async def get_all(params: RequestAllObject,
                 receiptService: ReceiptService = Depends(get_receipt_service)):
    return await receiptService.get_all(params)

@router.post(
    "/make_payment",
    response_model = ReceiptResponseSchema,
    status_code = 201,
    summary = "Провести оплату по чеку",
    description = "Регистрирует оплату по чеку. Если оплаченная сумма покрывает чек полностью, чек переходит в статус `paid`, создается транзакция дохода, а сотрудникам, оказавшим услуги, автоматически начисляется комиссия. Переплата зачисляется на депозит клиента, если `add_change_to_deposit` установлен в `true`.",
    dependencies=[Depends(require_permission([PermissionCode.RECEIPT_MAKE_PAYMENT]))]
)
async def make_payment(data: ReceiptPaymentCreateSchema,
                       receiptService: ReceiptService = Depends(get_receipt_service)):
    return await receiptService.make_payment(data)

@router.post(
    "/cancel",
    response_model=ReceiptResponseSchema,
    status_code=status.HTTP_200_OK,
    summary = "Отменить чек",
    description = "Отменяет чек по `id` (передается как query-параметр), отменяет связанные оплаты и комиссии, возвращает списанные товары на склад. Если по чеку уже проводилась оплата, отмена возможна только в течение периода, заданного в настройках организации (`cancel_payment_due`).",
    dependencies=[Depends(require_permission([PermissionCode.RECEIPT_CANCEL]))])
async def cancel(id: int, receiptService: ReceiptService = Depends(get_receipt_service)):
    return await receiptService.cancel(id)