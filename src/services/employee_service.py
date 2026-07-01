import math

from fastapi import HTTPException, status
from src.core.decorators.requireID import require_exists
from src.core.dependencies.uow import UnitOfWork
from src.repository.appointment.appointment_model import Appointment
from src.repository.employee.employee_model import Employee
from src.repository.payroll.payroll_model import Payroll
from src.schemas.base import PaginationSchema, RequestAllObject
from src.schemas.employee.create import EmployeeCreateSchema
from src.schemas.employee.update import EmployeeUpdateSchema

class EmployeeService():
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create(self, data: EmployeeCreateSchema) -> Employee:
        employee_data = data.model_dump()
        services_ids = employee_data.pop("services_ids", [])
        
        new_employee = Employee(**employee_data)
        
        if services_ids:
            found_services = await self.uow.services.get_by_ids(services_ids)
            
            if len(found_services) != len(services_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="One or more provided service_ids do not exist."
                )
                
            new_employee.services = found_services

        return await self.uow.employees.create(new_employee)
    
    async def get(self, id: int) -> Employee:
        result = await self.uow.employees.get(id)
        if result is None:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"Сотрудник с ID {id} не найден"
            )
        return result
    
    async def update(self, data: EmployeeUpdateSchema) -> Employee:
        services = None
        if data.services is not None and len(data.services) >= 1:
            services = await self.uow.services.get_by_ids(data.services)
            if len(services) != len(data.services):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Один или более из указанных услуг не найден"
                )
        dataDict = data.model_dump(exclude={"id"}, exclude_unset=True)
        result = await self.uow.employees.update(data.id, **dataDict)
        if result is None:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"Сотрудник с ID {id} не найден"
            )
        return result
    
    async def get_many(self, ids: list[int]) -> list[Employee]:
        return await self.uow.employees.get_by_ids(ids)
    
    async def get_all(self, data: RequestAllObject) -> dict:
        items, total_items = await self.uow.employees.get_all(data)

        total_pages = math.ceil(total_items / data.pageSize) if data.pageSize > 0 else 0
        
        return {
            "items": items,
            "page": data.page,
            "pageSize": data.pageSize,
            "totalItems": total_items,
            "totalPages": total_pages
        }
    
    async def delete(self, id: int) -> bool:
        return await self.uow.employees.delete(id)
    
    @require_exists("employees")
    async def get_workSchedules(self, id: int):
        return await self.uow.work_schedules.get_workSchedules(id)
    
    @require_exists("employees")
    async def get_payrolls(self, data: PaginationSchema, id: int) -> dict:
        items, total_items = await self.uow.payrolls.get_by_employee(data, id)

        total_pages = math.ceil(total_items / data.pageSize) if data.pageSize > 0 else 0
        
        return {
            "items": items,
            "page": data.page,
            "pageSize": data.pageSize,
            "totalItems": total_items,
            "totalPages": total_pages
        }
    
    @require_exists("employees")
    async def get_appointments(self, data: PaginationSchema, id: int) -> dict:
        items, total_items = await self.uow.appointments.get_by_employee(data, id)

        total_pages = math.ceil(total_items / data.pageSize) if data.pageSize > 0 else 0
        
        return {
            "items": items,
            "page": data.page,
            "pageSize": data.pageSize,
            "totalItems": total_items,
            "totalPages": total_pages
        }