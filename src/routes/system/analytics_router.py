from fastapi import APIRouter, Depends
from src.core.dependencies.uow import make_service_dependency
from src.schemas.analytics.appointmentResponse import ApppointmentAnalyticsResponse
from src.schemas.analytics.receiptResponse import ReceiptAnalyticsResponse
from src.schemas.analytics.request import GetReportWithFilters
from src.services.appointment.appointment_service import AppointmentService
from src.services.payment.receipt_service import ReceiptService

router = APIRouter()

get_receipt_service = make_service_dependency(ReceiptService)
get_appointment_service = make_service_dependency(AppointmentService)

@router.post(
    "/receipts",
    status_code = 200,
    response_model = ReceiptAnalyticsResponse)
async def login(data: GetReportWithFilters,
                receiptService: ReceiptService = Depends(get_receipt_service)):
    return await receiptService.get_analytics(data)

@router.post(
    "/appointments",
    status_code = 200,
    response_model = ApppointmentAnalyticsResponse)
async def login(data: GetReportWithFilters,
                appointmentService: AppointmentService = Depends(get_appointment_service)):
    return await appointmentService.get_analytics(data)