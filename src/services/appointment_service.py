import math
from multiprocessing.connection import Client
from fastapi import HTTPException, status
from sqlalchemy import select
from src.core.decorators.requireID import require_exists
from src.core.dependencies.uow import UnitOfWork
from src.repository.appointment.appointment_model import Appointment, AppointmentStatus
from src.repository.employee.employee_model import Employee
from src.repository.service.service_model import Service
from src.schemas.appointment.create import AppointmentCreateSchema
from src.schemas.appointment.response import AppointmentResponseSchema, ClientNestedResponseSchema
from src.schemas.base import RequestAllObject

class AppointmentService():
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        
    @require_exists("clients", target_param = "client_id")
    async def create(self, data: AppointmentCreateSchema) -> Appointment:
        existing = await self.uow.appointments.client_has_overlap(
            data.client_id, data.start_time_est, data.end_time_est)
        
        if existing: raise HTTPException(status_code = 409, detail = "Appointment slot already taken by this client")
        
        for record in (data.records or []):
            employee = await self.uow.employees.get(record.employee_id)
            if not employee:
                raise HTTPException(
                    status_code = status.HTTP_404_NOT_FOUND,
                    detail = f"Employee with id {data.id} not found"
                )
            if not employee.active:
                raise HTTPException(
                    status_code = status.HTTP_400_BAD_REQUEST,
                    detail = f"Employee with id {data.id} is inactive"
                )
            
            isWorking = await self.uow.work_schedules.is_employee_working(employee.id, data.start_time_est, data.end_time_est)
            if not isWorking:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Employee {employee.id} is not scheduled to work during these hours."
                )
            
            has_conflict = await self.uow.appointmentRecords.employee_has_overlap(
                employee.id, data.start_time_est, data.end_time_est
            )
            if has_conflict:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Employee {employee.firstname} is already booked during this time frame."
                )
            
            employeeAllowedServices = {i.id for i in employee.services}
            for service in record.services:
                if service.service_id:
                    serviceObj = await self.uow.services.get(service.service_id)
                    if not serviceObj:
                        raise HTTPException(
                            status_code = 404,
                            detail = f"Service with id {data.id} not found"
                        )
                    
                    if serviceObj.id not in employeeAllowedServices:
                        raise HTTPException(
                            status_code = 400,
                            detail = f"Employee {employee.id} does not provide services: {service.id}"
                        )
                    
                    if service.price is None: service.price = serviceObj.price
                    if service.price != serviceObj.price and (service.price_changed_reason is None or len(service.price_changed_reason.strip()) == 0):
                        raise HTTPException(
                            status_code = 400,
                            detail = f"Необходимо в комментариях указать причину изменения стоимости услуги"
                        )
                if service.material_id:
                    materialObj = await self.uow.materials.get(service.material_id)
                    if not materialObj:
                        raise HTTPException(
                            status_code = 404,
                            detail = f"Service with id {data.id} not found"
                        )
                    if service.quantity > materialObj.quantity:
                        raise HTTPException(
                            status_code = 400,
                            detail = f"Недостаточное количество {materialObj.article} {materialObj.name} на складе, требуется {service.quantity}, на складе: {materialObj.quantity}"
                        )
                    if service.price is None: service.price = materialObj.price
                    if service.price != materialObj.price and (service.notes is None or len(service.notes.strip()) == 0):
                        raise HTTPException(
                            status_code = 400,
                            detail = f"Необходимо в комментариях указать причину изменения стоимости товара"
                        )
        return await self.uow.appointments.create(data)
    
    async def get(self, id: int) -> Appointment:
        appointment = await self.uow.appointments.get(id)
        if appointment is None:
            raise HTTPException(status_code = 404, detail = f"Посещение с ID {id} не найден")
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
    
    async def cancel(self, id: int) -> Appointment:
        appointment = await self.uow.appointments.get(id)
        if not appointment:
            raise HTTPException(
                status_code = 404,
                detail = f"Посещение с ID {id} не найден"
            )
        
        if appointment.status == AppointmentStatus.CANCELLED:
            raise HTTPException(
                status_code = 400,
                detail = f"Посещение уже отменено"
            )
        
        if appointment.paid:
            raise HTTPException(
                status_code = 400,
                detail = f"Нельзя отменить оплаченое посещение. Сначало отмените оплату и уже после само посещение"
            )
        
        return await self.uow.appointments.cancel(appointment)

    async def delete(self, id: int) -> bool:
        result = await self.uow.appointments.delete(id)
        if not result:
            raise HTTPException(
                status_code = 404,
                detail = f"Посещение с ID {id} не найден"
            )
        return True