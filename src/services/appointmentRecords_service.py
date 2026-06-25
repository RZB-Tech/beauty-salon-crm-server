import math
from fastapi import HTTPException, status
from src.core.decorators.requireID import require_exists
from src.core.dependencies.uow import UnitOfWork
from src.repository.appointment.appointment_model import AppointmentRecords
from src.schemas.appointment.create import AppointmentRecordsCreateSchema
from src.schemas.base import RequestAllObject

class AppointmentRecordsService():
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        
    @require_exists("appointmentRecords", target_param = "appointment_id")
    async def create(self, data: AppointmentRecordsCreateSchema) -> AppointmentRecords:
        employee = await self.uow.employee.get(data.employee_id)
        if not employee:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"Employee with id {data.employee_id} not found"
            )
            
        employeeAllowedServices = {i.id for i in employee.services}
        for service in data.services:
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
                
        return await self.uow.appointmentRecords.create(data)

    
    # async def update(data: ClientUpdateSchema) -> Client:
    #     check = await appointmentRepository.get(data.id)
    #     if not check:
    #         raise HTTPException(
    #             status_code = status.HTTP_404_NOT_FOUND,
    #             detail = f"Service with id {data.id} not found"
    #         )
    #     result = await appointmentRepository.update(data)
    #     return result
    
    async def get(self, id: int) -> AppointmentRecords:
        result = await self.uow.appointmentRecords.get(id)
        if not result:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"Appointment record with id {id} not found"
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
    
    @require_exists("appointmentRecords")
    async def delete(self, id: int) -> bool:
        return await self.uow.appointmentRecords.delete(id)