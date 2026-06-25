from fastapi import APIRouter, Depends
from src.core.dependencies.auth import get_current_staff
from src.routes.employee_router import router as employeeR
from src.routes.service_router import router as serviceR
from src.routes.serviceCategory_router import router as serviceCategoryR
from src.routes.client_router import router as clientR
from src.routes.auth_router import router as authR
from src.routes.material_router import router as materialR
from src.routes.workSchedule_router import router as workScheduleR
from src.routes.absence_router import router as absenceR
from src.routes.appointment_router import router as appointmentR
from src.routes.payroll_router import router as payrollR
from src.routes.appointmentRecords_router import router as appointmentRecordsR
from src.routes.appointmentServices_router import router as appointmentServicesR
from src.routes.auditLogs_router import router as auditLogsR
from src.routes.receipt_router import router as ReceiptR
from src.routes.payment_router import router as PaymentR

open_router = APIRouter(prefix = "/api/v1")
open_router.include_router(
    authR, 
    prefix="/auth", 
    tags=["auth"]
)

protected_router = APIRouter(prefix = "/api/v1")

protected_router.dependencies.extend([
    Depends(get_current_staff)
])

protected_router.include_router(
    appointmentR, 
    prefix="/appointments", 
    tags=["appointments"]
)

protected_router.include_router(
    appointmentRecordsR, 
    prefix="/appointments-records", 
    tags=["appointments-records"]
)

protected_router.include_router(
    appointmentServicesR, 
    prefix="/appointments-services", 
    tags=["appointments-services"]
)

protected_router.include_router(
    employeeR, 
    prefix="/employees", 
    tags=["Employees"]
)

protected_router.include_router(
    workScheduleR, 
    prefix="/work-schedules", 
    tags=["Work schedules"]
)

protected_router.include_router(
    absenceR, 
    prefix="/absences", 
    tags=["Absences"]
)

protected_router.include_router(
    ReceiptR, 
    prefix="/receipts", 
    tags=["Receipts"]
)

protected_router.include_router(
    PaymentR, 
    prefix="/payments", 
    tags=["Payments"]
)

protected_router.include_router(
    payrollR, 
    prefix="/payrolls", 
    tags=["Payrolls"]
)

protected_router.include_router(
    clientR, 
    prefix="/clients", 
    tags=["Clients"]
)


protected_router.include_router(
    materialR, 
    prefix="/materials", 
    tags=["Materials"]
)

protected_router.include_router(
    serviceR, 
    prefix="/services", 
    tags=["Services"]
)

protected_router.include_router(
    serviceCategoryR, 
    prefix="/service-categories", 
    tags=["Service categories"]
)

protected_router.include_router(
    auditLogsR, 
    prefix="/audit-logs", 
    tags=["Audit logs"]
)