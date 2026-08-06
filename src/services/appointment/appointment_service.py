import math
from src.core.decorators.requireID import require_exists
from src.core.dependencies.uow import UnitOfWork
from src.exceptions.appointment_exceptions import AppointmentCancelled, AppointmentHasActiveReceipts, AppointmentIsPaid, AppointmentNotFound, ClientAppointmentConflict, EmployeeAppointmentConflict
from src.exceptions.employee_exceptions import EmployeeDoesNotProvideService, EmployeeDoesNotWork, EmployeeIsArchived, EmployeeNotFound
from src.exceptions.general_exceptions import CannotUpdate, PriceChangedReasonEmpty
from src.exceptions.material_exceptions import MaterialAmountInsufficient, MaterialArchived, MaterialNotFound
from src.exceptions.service_exceptions import ServiceIsArchived, ServiceNotFound
from src.repository.appointment.appointment_model import Appointment, AppointmentStatus
from src.repository.receipt.receipt_model import Receipt
from src.schemas.appointment.create import AppointmentCreateSchema
from src.schemas.appointment.update import AppointmentCancelSchema, AppointmentUpdateSchema
from src.schemas.base import RequestAllObject

class AppointmentService():
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        
    @require_exists("clients", target_param = "client_id")
    async def create(self, data: AppointmentCreateSchema) -> Appointment:
        existing = await self.uow.appointments.client_has_overlap(
            data.client_id, data.start_time_est, data.end_time_est)
        
        if existing: raise ClientAppointmentConflict()

        for record in (data.records or []):
            employee = await self.uow.employees.get(record.employee_id)
            if employee is None: raise EmployeeNotFound(record.employee_id)
            if not employee.active or employee.archived: raise EmployeeIsArchived(employee.id, employee.firstname)
            
            isWorking = await self.uow.work_schedules.is_employee_working(employee.id, data.start_time_est, data.end_time_est)
            if not isWorking: raise EmployeeDoesNotWork(employee.id, employee.firstname)

            has_conflict = await self.uow.appointmentRecords.employee_has_overlap(
                employee.id, data.start_time_est, data.end_time_est
            )
            if has_conflict: raise EmployeeAppointmentConflict(employee.id, employee.firstname)

            employeeAllowedServices = {i.id for i in employee.services}
            for service in record.services:
                if service.service_id:
                    serviceObj = await self.uow.services.get(service.service_id)
                    if not serviceObj: raise ServiceNotFound(service.service_id)
                    if serviceObj.archived: raise ServiceIsArchived(serviceObj.id, serviceObj.name)
                    if serviceObj.id not in employeeAllowedServices: raise EmployeeDoesNotProvideService(employee.id, employee.firstname, serviceObj.id, serviceObj.name)
                    
                    if service.price is None: service.price = serviceObj.price
                    if service.price != serviceObj.price and (service.price_changed_reason is None or len(service.price_changed_reason.strip()) == 0):
                        raise PriceChangedReasonEmpty()
                if service.material_id:
                    materialObj = await self.uow.materials.get(service.material_id)
                    if not materialObj: raise MaterialNotFound(service.material_id)
                    if materialObj.archived: raise MaterialArchived(materialObj.id, materialObj.name)
                    
                    if service.quantity > materialObj.quantity:
                        raise MaterialAmountInsufficient(materialObj.id, materialObj.name, service.quantity, materialObj.quantity)
                    if service.price is None: service.price = materialObj.sell_price
                    if service.price != materialObj.sell_price and (service.notes is None or len(service.notes.strip()) == 0):
                        raise PriceChangedReasonEmpty()
                    
        return await self.uow.appointments.create(data)
    
    async def update(self, data: AppointmentUpdateSchema) -> Appointment:
        checkIfExists = await self.uow.appointments.get(data.id)
        if checkIfExists is None: raise AppointmentNotFound(data.id)

        dataDict = data.model_dump(exclude={"id"}, exclude_unset=True)
        result = await self.uow.appointments.update(data.id, **dataDict)
        if result is None: raise CannotUpdate(data.id, "appointments")
        return result

    async def get(self, id: int) -> Appointment:
        appointment = await self.uow.appointments.get(id)
        if appointment is None: raise AppointmentNotFound(id)
        return appointment
    
    async def get_many(self, ids: list[int]) -> list[Appointment]:
        return await self.uow.appointments.get_by_ids(ids)
    
    async def get_all(self, data: RequestAllObject) -> dict:
        items, total_items = await self.uow.appointments.get_all(data)
        total_pages = math.ceil(total_items / data.pageSize) if data.pageSize > 0 else 0
        return {
            "items": items,
            "page": data.page,
            "pageSize": data.pageSize,
            "totalItems": total_items,
            "totalPages": total_pages
        }
    
    async def cancel(self, data: AppointmentCancelSchema) -> Appointment:
        appointment = await self.uow.appointments.get(data.id)
        if not appointment: raise AppointmentNotFound(data.id)

        if appointment.status == AppointmentStatus.CANCELLED: raise AppointmentCancelled(data.id)
        
        receipts = await self.uow.receipts.get_by_appointment(data.id, True)
        if len(receipts) >= 1: raise AppointmentHasActiveReceipts(data.id)
        
        if appointment.paid: raise AppointmentIsPaid(data.id)
        
        return await self.uow.appointments.update(data.id, status = AppointmentStatus.CANCELLED, cancelled_reason = data.reason)
    
    @require_exists("appointments")
    async def get_receipts(self, id: int) -> list[Receipt]:
        return await self.uow.receipts.get_by_appointment(id)