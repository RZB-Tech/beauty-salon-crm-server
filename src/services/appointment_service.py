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
        result = await self.uow.appointments.create(data)
        return result
    
    async def get(self, id: int) -> Appointment:
        appointment = await self.uow.appointments.get(id)
        if not appointment:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"Appointment with id {id} not found"
            )
        
        client_id = appointment.client_id
        employee_ids = { record.employee_id for record in appointment.records}
        service_ids = {
            srv.service_id
            for record in appointment.records
            for srv in record.services
            if srv.service_id is not None
        }

        appointment.client = await self.uow.clients.get(client_id)

        employees_map = {}
        if employee_ids:
            emp_stmt = select(Employee).where(Employee.id.in_(employee_ids))
            emp_res = await self.uow.db.execute(emp_stmt)
            employees_map = {emp.id: emp for emp in emp_res.scalars().all()}

        services_map = {}
        if service_ids:
            srv_stmt = select(Service).where(Service.id.in_(service_ids))
            srv_res = await self.uow.db.execute(srv_stmt)
            services_map = {srv.id: srv for srv in srv_res.scalars().all()}

        for record in appointment.records:
            record.employee = employees_map.get(record.employee_id)
            
            for srv in record.services:
                if srv.service_id:
                    srv.service = services_map.get(srv.service_id)
                else:
                    srv.service = None
        return appointment
    
    async def get_many(self, ids: list[int]) -> list[Appointment]:
        return await self.uow.appointments.get_by_ids(ids)
    
    async def get_all(self, data: RequestAllObject) -> dict:
        items, total_items = await self.uow.appointments.get_all(data)

        if items:
            all_client_ids = {i.client_id for i in items}
            all_employee_ids = set()
            all_service_ids = set()

            for i in items:
                for record in i.records:
                    all_employee_ids.add(record.employee_id)
                    for srv in record.services:
                        if srv.service_id is not None:
                            all_service_ids.add(srv.service_id)

            clients_map = {}
            if all_client_ids:
                client_res = await self.uow.clients.get_by_ids(all_client_ids)
                clients_map = {c.id: c for c in client_res}

            employees_map = {}
            if all_employee_ids:
                emp_res = await self.uow.employees.get_by_ids(all_employee_ids)
                employees_map = {e.id: e for e in emp_res}

            services_map = {}
            if all_service_ids:
                srv_res = await self.uow.services.get_by_ids(all_service_ids)
                services_map = {s.id: s for s in srv_res}

            # 3. 🌟 Map data and compute totals in memory (Blazing fast!)
            for i in items:
                i.client = clients_map.get(i.client_id)
                
                appointment_total = 0  # Running total for this specific appointment
                
                for record in i.records:
                    record.employee = employees_map.get(record.employee_id)
                    
                    for srv in record.services:
                        if srv.service_id:
                            srv.service = services_map.get(srv.service_id)
                        else:
                            srv.service = None
                        
                        # Accumulate the price multiplied by quantity
                        appointment_total += (srv.price * srv.quantity)
                
                # Dynamically attach the final calculation onto the appointment object
                i.total_price = appointment_total

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
        return result