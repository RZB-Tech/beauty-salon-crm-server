from fastapi import APIRouter, Depends, status
from src.core.dependencies.uow import make_service_dependency
from src.schemas.base import PaginatedResponseSchema, RequestAllObject
from src.schemas.transaction.create import TransactionCreateSchema
from src.schemas.transaction.response import TransactionResponseSchema
from src.services.transaction_service import TransactionService

router = APIRouter()
get_transaction_service = make_service_dependency(TransactionService)

@router.post(
    "/", 
    response_model=TransactionResponseSchema, 
    status_code = 201,
    summary="Create a new service"
)
async def create(data: TransactionCreateSchema,
                 transactionService: TransactionService = Depends(get_transaction_service)):
    return await transactionService.create(data)

@router.post(
    "/get-all",
    response_model=PaginatedResponseSchema[TransactionResponseSchema], 
    status_code = 200,
    summary="Get all categories"
)
async def get_all(params: RequestAllObject,
                 transactionService: TransactionService = Depends(get_transaction_service)):
    return await transactionService.get_all(params)

@router.get(
    "/{id}",
    response_model=TransactionResponseSchema, 
    status_code = 200,
    summary="Get "
)
async def get(id: int,
                 transactionService: TransactionService = Depends(get_transaction_service)):
    return await transactionService.get(id)

@router.post(
    "/{id}/cancel",
    response_model = TransactionResponseSchema,
    status_code = 200
)
async def cancel(id: int,
                 transactionService: TransactionService = Depends(get_transaction_service)):
    return await transactionService.cancel(id)