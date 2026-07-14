from fastapi import APIRouter, Depends, status
from src.core.dependencies.uow import  make_service_dependency
from src.schemas.base import PaginatedResponseSchema, RequestAllObject
from src.schemas.payout.create import PayoutCreateSchema
from src.schemas.payout.response import PayoutResponseSchema
from src.services.payment.payout_service import PayoutService

router = APIRouter()

get_payout_service = make_service_dependency(PayoutService)

@router.post(
    "", 
    response_model=PayoutResponseSchema, 
    status_code=status.HTTP_201_CREATED
)
async def create(data: PayoutCreateSchema,
                 payoutService: PayoutService = Depends(get_payout_service)):
    return await payoutService.create(data)

@router.post(
    "/get-all",
    response_model=PaginatedResponseSchema[PayoutResponseSchema], 
    status_code=status.HTTP_200_OK
)
async def get_all(params: RequestAllObject,
                 payoutService: PayoutService = Depends(get_payout_service)):
    return await payoutService.get_all(params)

@router.get(
    "/{id}",
    response_model=PayoutResponseSchema, 
    status_code=status.HTTP_200_OK
)
async def get(id: int,
                 payoutService: PayoutService = Depends(get_payout_service)):
    return await payoutService.get(id)