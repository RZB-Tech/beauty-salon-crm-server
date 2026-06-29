from src.database.session import get_repository_db, transaction_scope
from src.repository.appointment.appointmentRecords_repository import AppointmentRecordsRepository
from src.repository.appointment.appointment_repository import AppointmentRepository
from src.repository.appointment.appointmentServices_repository import AppointmentServicesRepository
from src.repository.audit.auditLog_repository import AuditLogsRepository
from src.repository.client.client_repository import ClientRepository
from src.repository.employee.absence_repository import EmployeeAbsenceRepository
from src.repository.employee.employee_repository import EmployeeRepository
from src.repository.employee.workSchedule_repository import WorkScheduleRepository
from src.repository.material.material_repository import MaterialRepository
from src.repository.payment.payment_repository import PaymentRepository
from src.repository.service.serviceCategory_repository import ServiceCategoryRepository
from src.repository.service.service_repository import ServiceRepository
from src.repository.staff.staff_repository import StaffRepository
from src.repository.payroll.payroll_repository import PayrollRepository
from src.repository.payroll.payout_repository import PayoutRepository
from src.repository.payment.receipt_repository import ReceiptRepository
from src.repository.transaction.transaction_repository import TransactionRepository
from src.repository.notification.notification_repository import NotificationRepository
from typing import Any, AsyncGenerator, TypeVar, Type, Callable

T = TypeVar("T")

class UnitOfWork:
    def __init__(self):
        self.staffs = StaffRepository()
        self.auditLogs = AuditLogsRepository()

        self.employees = EmployeeRepository()
        self.serviceCategory = ServiceCategoryRepository()
        self.services = ServiceRepository()
        self.work_schedules = WorkScheduleRepository()
        self.absences = EmployeeAbsenceRepository()
        self.clients = ClientRepository()
        self.materials = MaterialRepository()

        self.appointments = AppointmentRepository()
        self.appointmentRecords = AppointmentRecordsRepository()
        self.appointmentServices = AppointmentServicesRepository()

        self.payrolls = PayrollRepository()
        self.payouts = PayoutRepository()
        self.receipts = ReceiptRepository()
        self.payments = PaymentRepository()
        self.transactions = TransactionRepository()
        
        self.notifications = NotificationRepository()
    @property
    def db(self):
        return get_repository_db()

async def get_uow_with_context():
    """Single dependency that provides both session context AND uow."""
    yield UnitOfWork()

T = TypeVar("T")

def make_service_dependency(service_cls: Type[T]) -> Callable[..., AsyncGenerator[T, None]]:
    async def dependency() -> AsyncGenerator[T, None]:
        # This keeps the transaction open for the ENTIRE duration 
        # of the router request handling.
        async with transaction_scope():
            # Create a clean UnitOfWork instance bound to this specific request transaction context
            uow = UnitOfWork()
            yield service_cls(uow=uow)
            
    return dependency