from fastapi import APIRouter, Depends, HTTPException
from src.core.dependencies.auth import get_current_staff
from src.repository.registry import MODEL_REGISTRY, get_filter_schema
from src.routes.employee.employee_router import router as employeeR
from src.routes.employee.service_router import router as serviceR
from src.routes.employee.serviceCategory_router import router as serviceCategoryR
from src.routes.client.client_router import router as clientR
from src.routes.system.auth_router import router as authR
from src.routes.appointment.material_router import router as materialR
from src.routes.employee.workSchedule_router import router as workScheduleR
from src.routes.employee.absence_router import router as absenceR
from src.routes.appointment.appointment_router import router as appointmentR
from src.routes.payment.payroll_router import router as PayrollR
from src.routes.appointment.appointmentRecords_router import router as appointmentRecordsR
from src.routes.appointment.appointmentServices_router import router as appointmentServicesR
from src.routes.system.auditLogs_router import router as auditLogsR
from src.routes.payment.receipt_router import router as ReceiptR
from src.routes.payment.transaction_router import router as TransactionR
from src.routes.payment.payout_router import router as PayoutR
from src.routes.system.notification_router import router as notificationR
from src.routes.system.tenantPreferences_router import router as tenantPreferencesR
from src.routes.employee.specialization_router import router as specializationR
from src.schemas.base import FilterFieldSchema, FilterTables

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

@protected_router.get("/docs/filters/{table}", response_model = list[FilterFieldSchema])
async def get_table_filters(table: FilterTables):
    model = MODEL_REGISTRY.get(table.value)
    if model is None: raise HTTPException(404)
    return get_filter_schema(model)

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
    specializationR, 
    prefix="/specializations", 
    tags=["Specializations"]
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
    TransactionR, 
    prefix="/transactions", 
    tags=["Transactions"]
)

protected_router.include_router(
    ReceiptR, 
    prefix="/receipts", 
    tags=["Receipts"]
)

protected_router.include_router(
    PayrollR, 
    prefix="/payrolls", 
    tags=["Payrolls"]
)

protected_router.include_router(
    PayoutR,
    prefix = "/payouts",
    tags = ["Payouts"]
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
    notificationR,
    prefix = "/notifications",
    tags = ["Notifications"]
)

protected_router.include_router(
    tenantPreferencesR,
    prefix = "/tenant-preferences",
    tags = ["Tenant preferences"]
)

protected_router.include_router(
    auditLogsR, 
    prefix="/audit-logs", 
    tags=["Audit logs"]
)
