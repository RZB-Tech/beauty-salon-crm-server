from fastapi import APIRouter, Depends
from src.core.dependencies.uow import make_service_dependency
from src.schemas.analytics.receiptResponse import ReceiptAnalyticsResponse
from src.schemas.analytics.request import GetReportWithFilters
from src.services.payment.receipt_service import ReceiptService

router = APIRouter()

get_receipt_service = make_service_dependency(ReceiptService)

@router.post(
    "/receipts",
    status_code = 200,
    response_model = ReceiptAnalyticsResponse)
async def login(data: GetReportWithFilters,
                receiptService: ReceiptService = Depends(get_receipt_service)):
    return await receiptService.get_analytics(data)