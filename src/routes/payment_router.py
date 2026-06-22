from fastapi import APIRouter, Depends, status
from src.core.dependencies.uow import UnitOfWork, get_uow_with_context
from src.schemas.base import PaginatedResponseSchema, RequestAllObject
from src.schemas.payment.create import PaymentCreateSchema
from src.schemas.payment.response import PaymentResponseSchema, ReceiptResponseSchema
from src.services.payment_service import PaymentService

router = APIRouter()

def get_payment_service(uow: UnitOfWork = Depends(get_uow_with_context)) -> PaymentService:
    return PaymentService(uow=uow)

@router.post(
    "/", 
    response_model=ReceiptResponseSchema, 
    status_code=status.HTTP_201_CREATED
)
async def create(data: PaymentCreateSchema,
                 paymentService: PaymentService = Depends(get_payment_service)):
    return await paymentService.create(data)

# @router.patch(
#     "/",
#     response_model=MaterialResponseSchema, 
#     status_code=status.HTTP_200_OK,
#     summary="Update category"
# )
# async def update(data: MaterialUpdateSchema,
#                  materialService: MaterialService = Depends(get_material_service)):
#     return await materialService.update(data)

@router.post(
    "/get-all",
    response_model=PaginatedResponseSchema[PaymentResponseSchema], 
    status_code=status.HTTP_200_OK,
    summary="Get all categories"
)
async def get_all(params: RequestAllObject,
                 paymentService: PaymentService = Depends(get_payment_service)):
    return await paymentService.get_all(params)

@router.get(
    "/{id}",
    response_model=PaymentResponseSchema, 
    status_code=status.HTTP_200_OK,
    summary="Get "
)
async def get(id: int,
                 paymentService: PaymentService = Depends(get_payment_service)):
    return await paymentService.get(id)