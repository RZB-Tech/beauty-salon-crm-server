import math
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import raiseload
from src.core.decorators.requireID import require_exists
from src.core.dependencies.uow import UnitOfWork
from src.repository.appointment.appointment_model import Appointment, AppointmentServices
from src.repository.material.material_model import Material
from src.repository.payment.payment_model import Receipt, ReceiptStatus
from src.repository.service.service_model import Service
from src.schemas.appointment.create import AppointmentServicesCreateSchema
from src.schemas.appointment.update import AppointmentServiceUpdateSchema
from src.schemas.base import RequestAllObject

class AppointmentServicesService():
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
    
    async def create(self, data: AppointmentServicesCreateSchema) -> Appointment:
        appointmentRecord = await self.uow.appointmentRecords.get(data.appointment_record_id)
        if appointmentRecord is None: raise HTTPException(404, f"Записи по посещению с ID {data.appointment_record_id} не найден")
        appointmentID = appointmentRecord.appointment_id

        material: Material | None = None
        if data.material_id: 
            material = await self.uow.materials.get(data.material_id)
            if material is None: raise HTTPException(404, f"Товар с ID {data.material_id} не найден")
            if material.archived: raise HTTPException(409, f"Нельзя использовать архивированный Товар {material.name}, ID {material.id}")

        service: Service | None = None
        if data.service_id: 
            service = await self.uow.services.get(data.service_id)
            if service is None: raise HTTPException(404, f"Услуга с ID {data.service_id}")
            if service.archived: raise HTTPException(409, f"Нельзя использовать архивированную Услугу {service.name}, ID {service.id}")

        receipts = await self.uow.db.scalars(
            select(Receipt)
            .options(raiseload("*"))
            .where(Receipt.appointment_id == appointmentRecord.appointment_id)
        )
        if any(receipt.status != ReceiptStatus.CANCELLED for receipt in receipts):
            raise HTTPException(400, "Необходимо сначало отменить активный чек для этого посещения")
        
        employee = await self.uow.employees.get(appointmentRecord.employee_id)
        if not employee: raise HTTPException(404, f"Employee with id {data.employee_id} not found")
        
        if service is not None:
            employeeAllowedServices = {i.id for i in employee.services}
            if data.service_id not in employeeAllowedServices:
                raise HTTPException(409, f"Employee {employee.id} does not provide services: {service.id}")
            if data.price is None: data.price = service.price
            if data.price != service.price and (data.price_changed_reason is None or len(data.price_changed_reason.strip()) == 0):
                raise HTTPException(
                    status_code = 400,
                    detail = f"Необходимо указать причину изменения стоимости услуги"
                )
        
        if material is not None:
            if data.price is None: data.price = material.price
            if data.price != material.price and (data.price_changed_reason is None or len(data.price_changed_reason.strip()) == 0):
                raise HTTPException(
                    status_code = 400,
                    detail = f"Необходимо указать причину изменения стоимости товара"
                )

        newData = data.model_dump()
        newObject = AppointmentServices(**newData)
        await self.uow.appointmentServices.create(newObject)
        return await self.uow.appointments.get(appointmentID)
    
    async def update(self, data: AppointmentServiceUpdateSchema) -> Appointment:
        appointmentService = await self.uow.appointmentServices.get(data.id)
        if appointmentService is None: raise HTTPException(404)

        if (appointmentService.service_id and data.material_id) or (appointmentService.material_id and data.service_id): 
            raise HTTPException(400, "Запиь об оказанных услугах может содержать либо Услугу либо Товар")   
        
        appointmentRecord = appointmentService.appointment_record

        receipts = await self.uow.db.scalars(
            select(Receipt)
            .options(raiseload("*"))
            .where(Receipt.appointment_id == appointmentRecord.appointment_id)
        )
        if any(receipt.status != ReceiptStatus.CANCELLED for receipt in receipts):
            raise HTTPException(400, "Необходимо сначало отменить активный чек для этого посещения")
        
        material: Material | None = None
        if data.material_id: 
            material = await self.uow.materials.get(data.material_id)
            if material is None: raise HTTPException(404, f"Товар с ID {data.material_id} не найден")
            if material.archived: raise HTTPException(409, f"Нельзя использовать архивированный Товар {material.name}, ID {material.id}")

        service: Service | None = None
        if data.service_id: 
            service = await self.uow.services.get(data.service_id)
            if service is None: raise HTTPException(404, f"Услуга с ID {data.service_id}")
            if service.archived: raise HTTPException(409, f"Нельзя использовать архивированную Услугу {service.name}, ID {service.id}")
        
        employee = await self.uow.employees.get(appointmentRecord.employee_id)
        if not employee: raise HTTPException(404, f"Employee with id {data.employee_id} not found")
        
        if service is not None:
            employeeAllowedServices = {i.id for i in employee.services}
            if data.service_id not in employeeAllowedServices:
                raise HTTPException(
                    status_code = status.HTTP_404_NOT_FOUND,
                    detail = f"Employee {employee.id} does not provide services: {service.id}"
                )
            if data.price is None: data.price = service.price
            if data.price != service.price and (data.price_changed_reason is None or len(data.price_changed_reason.strip()) == 0):
                raise HTTPException(
                    status_code = 400,
                    detail = f"Необходимо указать причину изменения стоимости услуги"
                )
        
        if material is not None:
            if data.price is None: data.price = material.price
            if data.price != material.price and (data.price_changed_reason is None or len(data.price_changed_reason.strip()) == 0):
                raise HTTPException(
                    status_code = 400,
                    detail = f"Необходимо указать причину изменения стоимости товара"
                )
            
        dataDict = data.model_dump(exclude={"id"}, exclude_unset=True)
        await self.uow.appointmentServices.update(data.id, **dataDict)
        return await self.uow.appointments.get(appointmentRecord.appointment_id)
    
    async def get(self, id: int) -> AppointmentServices:
        result = await self.uow.appointmentServices.get(id)
        if result is None:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"Услуга из посещения с ID {id} не найдена"
            )
        return result
    
    async def get_many(self, ids: list[int]) -> list[AppointmentServices]:
        return await self.uow.appointmentsServices.get_by_ids(ids)
    
    async def get_all(self, data: RequestAllObject) -> dict:
        items, total_items = await self.uow.appointmentsServices.get_all(data)

        total_pages = math.ceil(total_items / data.pageSize) if data.pageSize > 0 else 0
        
        return {
            "items": items,
            "page": data.page,
            "pageSize": data.pageSize,
            "totalItems": total_items,
            "totalPages": total_pages
        }
    
    async def delete(self, id: int) -> Appointment:
        appointmentService = await self.uow.appointmentServices.get(id)
        if appointmentService is None: raise HTTPException(404)

        appointmentID = appointmentService.appointment_record.appointment_id

        receipts = await self.uow.db.scalars(
            select(Receipt)
            .options(raiseload("*"))
            .where(Receipt.appointment_id == appointmentID)
        )
        if any(receipt.status != ReceiptStatus.CANCELLED for receipt in receipts):
            raise HTTPException(400, "Необходимо сначало отменить активный чек для этого посещения")
        
        await self.uow.appointmentServices.delete(id)
        return await self.uow.appointments.get(appointmentID)