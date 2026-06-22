from fastapi import APIRouter, Depends, status
from src.core.dependencies.uow import UnitOfWork, get_uow_with_context
from src.schemas.base import PaginatedResponseSchema, RequestAllObject
from src.schemas.payment.create import ReceiptCreateSchema
from src.schemas.payment.response import ReceiptResponseSchema
from src.services.receipt_service import ReceiptService

router = APIRouter()

def get_receipt_service(uow: UnitOfWork = Depends(get_uow_with_context)) -> ReceiptService:
    return ReceiptService(uow=uow)

@router.post(
    "/", 
    response_model=ReceiptResponseSchema, 
    status_code=status.HTTP_201_CREATED
)
async def create(data: ReceiptCreateSchema,
                 receiptService: ReceiptService = Depends(get_receipt_service)):
    return await receiptService.create(data)

@router.post(
    "/get-all",
    response_model=PaginatedResponseSchema[ReceiptResponseSchema], 
    status_code=status.HTTP_200_OK,
    summary="Get all categories"
)
async def get_all(params: RequestAllObject,
                 receiptService: ReceiptService = Depends(get_receipt_service)):
    return await receiptService.get_all(params)

@router.post(
    "/cancel",
    response_model=ReceiptResponseSchema, 
    status_code=status.HTTP_200_OK)
async def cancel(id: int, receiptService: ReceiptService = Depends(get_receipt_service)):
    return await receiptService.cancel(id)