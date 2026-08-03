import math
from fastapi import HTTPException, status
from sqlalchemy import select
from src.core.decorators.requireID import require_exists
from src.core.dependencies.uow import UnitOfWork
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
        
        if existing: raise HTTPException(status_code = 409, detail = "Данный клиент уже записан на это время")

        for record in (data.records or []):
            employee = await self.uow.employees.get(record.employee_id)
            if employee is None:
                raise HTTPException(
                    status_code = 404,
                    detail = f"Сотрудник с ID {record.employee_id} не найден"
                )
            if not employee.active or employee.archived:
                raise HTTPException(
                    status_code = status.HTTP_400_BAD_REQUEST,
                    detail = f"Этого сотрудник {employee.firstname}, ID {employee.id} неактивен / архивирован"
                )
            
            isWorking = await self.uow.work_schedules.is_employee_working(employee.id, data.start_time_est, data.end_time_est)
            if not isWorking:
                raise HTTPException(
                    status_code= 409,
                    detail=f"Сотрудник {employee.id} не работает в указанное время"
                )

            has_conflict = await self.uow.appointmentRecords.employee_has_overlap(
                employee.id, data.start_time_est, data.end_time_est
            )
            if has_conflict:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Сотрудник {employee.firstname} уже занят в указанное время"
                )

            employeeAllowedServices = {i.id for i in employee.services}
            for service in record.services:
                if service.service_id:
                    serviceObj = await self.uow.services.get(service.service_id)
                    if not serviceObj:
                        raise HTTPException(
                            status_code = 404,
                            detail = f"Услуга с ID {service.service_id} не найдена"
                        )

                    if serviceObj.archived:
                        raise HTTPException(409, f"Нельзя использовать архивированную услугу {serviceObj.name}, ID {serviceObj.id}")

                    if serviceObj.id not in employeeAllowedServices:
                        raise HTTPException(409, f"Сотрудник {employee.id} не оказывает услугу с ID {serviceObj.id}")
                    
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
                            detail = f"Товар с ID {service.material_id} не найден"
                        )
                    if materialObj.archived:
                        raise HTTPException(409, f"Нельзя использовать архивированный Товар {materialObj.name}, ID {materialObj.id}")
                    
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
        return await self.uow.appointments.create(data)
    
    async def update(self, data: AppointmentUpdateSchema) -> Appointment:
        dataDict = data.model_dump(exclude={"id"}, exclude_unset=True)
        appointment = await self.uow.appointments.get(data.id)
        if not appointment: raise HTTPException(404,f"Посещение с ID {data.id} не найден")
        
        if dataDict.get("archived"):
            receipts = await self.uow.receipts.get_by_appointment(data.id, True)
            if len(receipts) >= 1: raise HTTPException(409, f"Нельзя архивировать посещение с активным чеков, сначала отмените чек.")
            if appointment.paid: raise HTTPException(409,f"Нельзя архивировать оплаченое посещение. Сначала отмените чек и уже после само посещение")
            
        result = await self.uow.appointments.update(data.id, **dataDict)
        if result is None: raise HTTPException(404, detail = f"Посещение с ID {data.id} не найден")
        return result

    async def get(self, id: int) -> Appointment:
        appointment = await self.uow.appointments.get(id)
        if appointment is None: raise HTTPException(status_code = 404, detail = f"Посещение с ID {id} не найден")
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
        if not appointment:
            raise HTTPException(
                status_code = 404,
                detail = f"Посещение с ID {data.id} не найден"
            )

        if appointment.status == AppointmentStatus.CANCELLED:
            raise HTTPException(
                status_code = 409,
                detail = f"Посещение уже отменено"
            )
        
        receipts = await self.uow.receipts.get_by_appointment(data.id, True)
        if len(receipts) >= 1: raise HTTPException(409, f"Нельзя отменить посещение с активным чеков, сначала отмените чек.")
        
        if appointment.paid:
            raise HTTPException(
                status_code = 409,
                detail = f"Нельзя отменить оплаченое посещение. Сначала отмените чек и уже после само посещение"
            )
        
        return await self.uow.appointments.update(data.id, status = AppointmentStatus.CANCELLED, cancelled_reason = data.reason)

    async def delete(self, id: int) -> bool:
        check = await self.uow.appointments.get(id)
        if check is None: raise HTTPException(404)
        if not check.archived: raise HTTPException(400, "Прежде чем удалить объект, необходимо его сначала заархировать.")
        await self.uow.appointments.delete(id)
        return True
    
    @require_exists("appointments")
    async def get_receipts(self, id: int) -> list[Receipt]:
        return await self.uow.receipts.get_by_appointment(id)