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
                service = await self.uow.services.get(service.service_id)
                if not service:
                    raise HTTPException(
                        status_code = status.HTTP_404_NOT_FOUND,
                        detail = f"Service with id {service.service_id} not found"
                    )
                
                if service.id not in employeeAllowedServices:
                    raise HTTPException(
                        status_code = status.HTTP_404_NOT_FOUND,
                        detail = f"Employee {employee.id} does not provide services: {service.service_id}"
                    )
                
            if service.material_id:
                material = await self.uow.materials.get(service.material_id)
                if not material:
                    raise HTTPException(
                        status_code = status.HTTP_404_NOT_FOUND,
                        detail = f"Material with id {service.material_id} not found"
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