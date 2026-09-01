from fastapi import APIRouter, Depends
from src.core.dependencies.uow import make_service_dependency
from src.schemas.analytics.appointmentResponse import ApppointmentAnalyticsResponse
from src.schemas.analytics.employeeResponse import EmployeeAnalyticsResponse
from src.schemas.analytics.receiptResponse import ReceiptAnalyticsResponse
from src.schemas.analytics.request import GetReportWithFilters, TranscationsByPeriod
from src.schemas.analytics.serviceResponse import ServiceAnalyticsResponse
from src.schemas.analytics.transationResponse import TransactionAnalyticsResponse, TransactionByPeriodResponse
from src.services.appointment.appointment_service import AppointmentService
from src.services.employee.employee_service import EmployeeService
from src.services.employee.service_service import ServiceService
from src.services.payment.receipt_service import ReceiptService
from src.services.payment.transaction_service import TransactionService

router = APIRouter()

get_receipt_service = make_service_dependency(ReceiptService)
get_appointment_service = make_service_dependency(AppointmentService)
get_transaction_service = make_service_dependency(TransactionService)
get_employee_service = make_service_dependency(EmployeeService)
get_service_service = make_service_dependency(ServiceService)

@router.post(
    "/receipts/kpi",
    status_code = 200,
    response_model = ReceiptAnalyticsResponse)
async def login(data: GetReportWithFilters,
                receiptService: ReceiptService = Depends(get_receipt_service)):
    return await receiptService.get_analytics(data)

@router.post(
    "/appointments/kpi",
    status_code = 200,
    response_model = ApppointmentAnalyticsResponse)
async def login(data: GetReportWithFilters,
                appointmentService: AppointmentService = Depends(get_appointment_service)):
    return await appointmentService.get_analytics(data)

@router.post(
    "/transactions/kpi",
    status_code = 200,
    response_model = TransactionAnalyticsResponse)
async def login(data: GetReportWithFilters,
                transactionService: TransactionService = Depends(get_transaction_service)):
    return await transactionService.get_analytics(data)

@router.post(
    "/transactions/by-period",
    status_code = 200,
    response_model = TransactionByPeriodResponse)
async def login(data: TranscationsByPeriod,
                transactionService: TransactionService = Depends(get_transaction_service)):
    return await transactionService.get_revenue_by_period(data)

@router.post(
    "/employees/kpi",
    status_code = 200,
    response_model = EmployeeAnalyticsResponse)
async def login(data: GetReportWithFilters,
                employeeService: EmployeeService = Depends(get_employee_service)):
    return await employeeService.get_analytics(data)

@router.post(
    "/services/kpi",
    status_code = 200,
    response_model = ServiceAnalyticsResponse)
async def login(data: GetReportWithFilters,
                serviceService: ServiceService = Depends(get_service_service)):
    return await serviceService.get_analytics(data)