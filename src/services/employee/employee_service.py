from io import BytesIO
import json
import math

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse, StreamingResponse
from openpyxl import Workbook
from src.core.decorators.requireID import require_exists
from src.core.dependencies.uow import UnitOfWork
from src.repository.employee.employee_model import Employee
from src.schemas.base import PaginationSchema, RequestAllObject
from src.schemas.employee.create import EmployeeCreateSchema
from src.schemas.employee.update import EmployeeUpdateSchema
from src.services.employee.workSchedule_service import WorkScheduleService

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
                raise HTTPException(404, detail="Одна или несколько указанных услуг не найдены")
                
            new_employee.services = found_services

        if data.specialization_id:
            specialization = await self.uow.specializations.get(data.specialization_id)
            if specialization is None: raise HTTPException(404, f"Специализация с ID {data.specialization_id} не найдена")
            if specialization.archived: raise HTTPException(409, f"Нельзя использовать архивированную специализацию")

        result = await self.uow.employees.create(new_employee)
        return await self.uow.employees.get(result.id)
    
    async def get(self, id: int) -> Employee:
        result = await self.uow.employees.get(id)
        if result is None:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"Сотрудник с ID {id} не найден"
            )
        return result
    
    async def update(self, data: EmployeeUpdateSchema) -> Employee:
        checkArchived = await self.uow.employees.get(data.id)
        if checkArchived.archived: raise HTTPException(409, detail = f"Сотрудник с ID {data.id} архивирован и не может быть изменен")

        dataDict = data.model_dump(exclude={"id"}, exclude_unset=True)
        if data.services is not None:
            services = []
            if len(data.services) >= 1:
                services = await self.uow.services.get_by_ids(data.services)
                if len(services) != len(data.services):
                    raise HTTPException( 404, detail="Один или более из указанных услуг не найден")
                for service in services: 
                    if service.archived: raise HTTPException(409, f"Нельзя привязать архивированную услугу {service.name} (ID {service.id}) к сотруднику")
            dataDict["services"] = services

        if data.specialization_id:
            specialization = await self.uow.specializations.get(data.specialization_id)
            if specialization is None: raise HTTPException(404, f"Специализация с ID {data.specialization_id} не найдена")
            if specialization.archived: raise HTTPException(409, f"Нельзя использовать архивированную специализацию")
        
        result = await self.uow.employees.update(data.id, **dataDict)
        if result is None:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"Сотрудник с ID {data.id} не найден"
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
    async def get_workSchedules(self, id: int) -> dict:
        result = await self.uow.work_schedules.get_workSchedules(id)
        return {
            "work_schedules": [
                WorkScheduleService._to_response_schedule(schedule)
                for schedule in result["work_schedules"]
            ],
            "absences": result["absences"]
        }
    
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

    def _export_excel(self, employees: list[dict]):
        wb = Workbook()
        ws = wb.active
        ws.title = "Employees"

        headers = [
            "ID",
            "First name",
            "Last name",
            "Middle name",
            "Phone",
            "Birth date",
            "Active",
            "Specialization",
            "Salary",
            "% Services",
            "% Sales",
            "Services",
            "Notes",
        ]

        ws.append(headers)

        for emp in employees:
            ws.append([
                emp["id"],
                emp["firstname"],
                emp["lastname"],
                emp["middlename"],
                emp["phone"],
                emp["birth_date"],
                "Yes" if emp["active"] else "No",
                emp["specialization"],
                emp["salary_fixed"],
                emp["percent_from_services"],
                emp["percent_from_sales"],
                ", ".join(emp["services"]),
                emp["notes"],
            ])

        stream = BytesIO()
        wb.save(stream)
        stream.seek(0)

        return StreamingResponse(
            stream,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": 'attachment; filename="employees.xlsx"'
            }, 
        )  

    def _export_json(self, data: list[dict]):
        stream = BytesIO()

        stream.write(
            json.dumps(
                data,
                ensure_ascii=False,  # preserve Unicode
                indent=2,
            ).encode("utf-8")
        )
        stream.seek(0)

        return StreamingResponse(
            stream,
            media_type="application/json",
            headers={
                "Content-Disposition": 'attachment; filename="employees.json"',
            },
        )

    async def export(self, format: str):
        employees = await self.uow.employees.get_all_for_export()

        data = [
            {
                "id": e.id,
                "firstname": e.firstname,
                "lastname": e.lastname,
                "middlename": e.middlename,
                "phone": e.phone,
                "birth_date": e.birth_date.isoformat(),
                "active": e.active,
                "specialization": (
                    e.specialization.name
                    if e.specialization
                    else None
                ),
                "salary_fixed": e.salary_fixed,
                "percent_from_services": e.percent_from_services,
                "percent_from_sales": e.percent_from_sales,
                "services": [s.name for s in e.services],
                "notes": e.notes,
            }
            for e in employees
        ]

        if format == "json":
            return self._export_json(data)

        return self._export_excel(data)