import math
from fastapi import HTTPException, status
from sqlalchemy.orm import raiseload
from src.core.decorators.requireID import require_exists
from src.core.dependencies.uow import UnitOfWork
from src.repository.appointment.appointment_model import Appointment, AppointmentRecords
from src.repository.material.material_model import Material
from src.repository.payment.payment_model import Receipt, ReceiptStatus
from src.repository.service.service_model import Service
from src.schemas.appointment.create import AppointmentRecordsCreateSchema
from src.schemas.base import RequestAllObject
from sqlalchemy import select

class AppointmentRecordsService():
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        
    @require_exists("appointments", target_param = "appointment_id")
    async def create(self, data: AppointmentRecordsCreateSchema) -> Appointment:
        receipts = await self.uow.db.scalars(
            select(Receipt)
            .options(raiseload("*"))
            .where(Receipt.appointment_id == data.appointment_id)
        )
        if any(receipt.status != ReceiptStatus.CANCELLED for receipt in receipts):
            raise HTTPException(400, "Необходимо сначало отменить активный чек для этого посещения")

        employee = await self.uow.employees.get(data.employee_id)
        if not employee:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"Сотрудник с ID {data.employee_id} не найден"
            )
        if not employee.active or employee.archived:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = f"Этого сотрудник {employee.firstname}, ID {employee.id} неактивен / архивирован"
            )
            
        employeeAllowedServices = {i.id for i in employee.services}
        for service in data.services:
            if service.service_id:
                serviceObj = await self.uow.services.get(service.service_id)
                if not serviceObj:
                    raise HTTPException(
                        status_code = 404,
                        detail = f"Service with id {service.service_id} not found"
                    )
                if serviceObj.archived: 
                        raise HTTPException(409, f"Нельзя использовать архивированную услуг {serviceObj.name}, ID {serviceObj.id}")
                
                if serviceObj.id not in employeeAllowedServices:
                    raise HTTPException(
                        status_code = 409,
                        detail = f"Employee {employee.id} does not provide services: {service.service_id}"
                    )
                
                if service.price is None: service.price = serviceObj.price
                if service.price != serviceObj.price and (service.notes is None or len(service.notes.strip()) == 0):
                    raise HTTPException(
                        status_code = 400,
                        detail = f"Необходимо в комментариях указать причину изменения стоимости услуги"
                    )
            if service.material_id:
                materialObj = await self.uow.materials.get(service.material_id)
                if not materialObj:
                    raise HTTPException(
                        status_code = 404,
                        detail = f"Material with id {service.material_id} not found"
                    )
                if materialObj.archived: 
                    raise HTTPException(409, f"Нельзя использовать архивированную услуг {materialObj.name}, ID {materialObj.id}")
                if service.quantity > materialObj.quantity:
                    raise HTTPException(
                        status_code = 400,
                        detail = f"Недостаточное количество {materialObj.article} {materialObj.name} на складе, требуется {service.quantity}, на складе: {materialObj.quantity}"
                    )
                if service.price is None: service.price = materialObj.sell_price
                if service.price != materialObj.sell_price and (service.notes is None or len(service.notes.strip()) == 0):
                    raise HTTPException(
                        status_code = 400,
                        detail = f"Необходимо в комментариях указать причину изменения стоимости товара"
                    )
                
        await self.uow.appointmentRecords.create(data)
        return await self.uow.appointments.get(data.appointment_id)
    
    async def get(self, id: int) -> AppointmentRecords:
        result = await self.uow.appointmentRecords.get(id)
        if result is None:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"Запись из посещения с ID {id} не найдена"
            )
        return result
    
    async def get_many(self, ids: list[int]) -> list[AppointmentRecords]:
        return await self.uow.appointmentRecords.get_by_ids(ids)
    
    async def get_all(self, data: RequestAllObject) -> dict:
        items, total_items = await self.uow.appointmentRecords.get_all(data)

        total_pages = math.ceil(total_items / data.pageSize) if data.pageSize > 0 else 0
        
        return {
            "items": items,
            "page": data.page,
            "pageSize": data.pageSize,
            "totalItems": total_items,
            "totalPages": total_pages
        }
    
    async def delete(self, id: int) -> Appointment:
        check = await self.uow.appointmentRecords.get(id)
        if check is None: raise HTTPException(404)

        receipts = await self.uow.db.scalars(
            select(Receipt)
            .options(raiseload("*"))
            .where(Receipt.appointment_id == check.appointment_id)
        )

        if any(receipt.status != ReceiptStatus.CANCELLED for receipt in receipts):
            raise HTTPException(400, "Необходимо сначало отменить активный чек для этого посещения")
        
        appointmentID = check.appointment_id

        await self.uow.appointmentRecords.delete(id)
        return await self.uow.appointments.get(appointmentID)
    