from pydantic import BaseModel
from enum import Enum

class Tables(Enum):
    appointments = "appointments"
    appointment_records = "appointment_records"
    appointment_services = "appointment_services"
    clients = "clients"
    employees = "employees"
    employee_absences = "employee_absences"
    employee_work_schedules = "employee_work_schedules"
    materials = "materials"
    payments = "payments"
    payrolls = "payrolls"
    payouts = "payouts"
    transactions = "transactions"
    receipt_items = "receipt_items"
    receipts = "receipts"
    service_categories = "service_categories"
    services = "services"
    specializations = "specializations"
    staffs = "staffs"
    notifications = "notifications"

class AuditLogsRequestSchema(BaseModel):
    table_name: Tables
    record_id: int
