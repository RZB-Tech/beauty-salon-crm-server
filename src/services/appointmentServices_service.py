import math
from fastapi import HTTPException, status
from src.core.decorators.requireID import require_exists
from src.core.dependencies.uow import UnitOfWork
from src.repository.appointment.appointment_model import AppointmentServices
from src.schemas.appointment.create import AppointmentServicesCreateSchema
from src.schemas.base import RequestAllObject

class AppointmentServicesService():
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
    
    @require_exists("appointmentRecords", target_param = "appointment_record_id")
    @require_exists("services", target_param = "service_id")
    @require_exists("materials", target_param = "material_id")
    async def create(self, data: AppointmentServicesCreateSchema) -> AppointmentServices:
        appointmentRecord = await self.uow.appointmentRecords.get(data.appointment_record_id)
        service = await self.uow.services.get(data.service_id)

        employee = await self.uow.employees.get(appointmentRecord.employee_id)
        if not employee:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"Employee with id {data.employee_id} not found"
            )
        
        employeeAllowedServices = {i.id for i in employee.services}
        if data.service_id not in employeeAllowedServices:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"Employee {employee.id} does not provide services: {service.id}"
            )

        newData = data.model_dump()
        newObject = AppointmentServices(**newData)
        return await self.uow.appointmentServices.create(newObject)

    
    # async def update(data: ClientUpdateSchema) -> Client:
    #     check = await appointmentRepository.get(data.id)
    #     if not check:
    #         raise HTTPException(
    #             status_code = status.HTTP_404_NOT_FOUND,
    #             detail = f"Service with id {data.id} not found"
    #         )
    #     result = await appointmentRepository.update(data)
    #     return result
    
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
    
    @require_exists("appointmentServices")
    async def delete(self, id: int) -> bool:
        return await self.uow.appointmentsServices.delete(id)