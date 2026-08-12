import math
from sqlalchemy.orm import raiseload
from src.core.decorators.requireID import require_exists
from src.core.dependencies.uow import UnitOfWork
from src.exceptions.appointment_exceptions import AppointmentHasActiveReceipts, AppointmentRecordNotFound
from src.exceptions.employee_exceptions import EmployeeDoesNotProvideService, EmployeeInactive, EmployeeIsArchived, EmployeeNotFound
from src.exceptions.general_exceptions import PriceChangedReasonEmpty
from src.exceptions.service_exceptions import ServiceIsArchived, ServiceNotFound
from src.exceptions.material_exceptions import MaterialNotFound, MaterialArchived, MaterialAmountInsufficient
from src.repository.appointment.appointment_model import Appointment, AppointmentRecords
from src.repository.promotion.promotion_model import PromotionType
from src.repository.receipt.receipt_model import Receipt, ReceiptStatus
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
            raise AppointmentHasActiveReceipts(data.appointment_id)

        employee = await self.uow.employees.get(data.employee_id)
        if employee is None: raise EmployeeNotFound(data.employee_id)
        if not employee.active: raise EmployeeInactive(data.employee_id, employee.firstname)
        if employee.archived: raise EmployeeIsArchived(data.employee_id, employee.firstname)
            
        employeeAllowedServices = {i.id for i in employee.services}
        price_info: list[dict] = []
        for service in data.services:
            info = {"base_price": 0, "final_price": 0, "promotion_id": None}
            if service.service_id:
                serviceObj = await self.uow.services.get(service.service_id)
                if serviceObj is None: raise ServiceNotFound(service.service_id)
                if serviceObj.archived: raise ServiceIsArchived(service.service_id, serviceObj.name)
                if serviceObj.id not in employeeAllowedServices:
                    raise EmployeeDoesNotProvideService(employee.id, employee.firstname, serviceObj.id, serviceObj.name)
                if (service.price != serviceObj.price and service.price is not None) and (service.price_changed_reason is None or len(service.price_changed_reason.strip()) == 0):
                    raise PriceChangedReasonEmpty()

                info["base_price"] = serviceObj.price if service.price is None else service.price
                info["final_price"] = info["base_price"]

                hasPromotion = await self.uow.promotions.get_by_object(serviceObj.id, "service")
                if hasPromotion is not None:
                    info["promotion_id"] = hasPromotion.id
                    if hasPromotion.promo_type == PromotionType.FIXED_AMOUNT and hasPromotion.discount_value:
                        discount = info["base_price"] - hasPromotion.discount_value
                        info["final_price"] = discount if discount >= 0 else 0
                    elif hasPromotion.promo_type == PromotionType.PERCENTAGE and hasPromotion.discount_value:
                        discount = info["base_price"] * (hasPromotion.discount_value / 100)
                        info["final_price"] = info["base_price"] - discount
                
            if service.material_id:
                materialObj = await self.uow.materials.get(service.material_id)
                if materialObj is None: raise MaterialNotFound(service.material_id)
                if materialObj.archived: raise MaterialArchived(materialObj.id, materialObj.name)
                if service.quantity > materialObj.quantity:
                    raise MaterialAmountInsufficient(materialObj.id, materialObj.name, service.quantity, materialObj.quantity)
                if service.price != materialObj.sell_price and (service.notes is None or len(service.notes.strip()) == 0):
                    raise PriceChangedReasonEmpty()

                info["base_price"] = materialObj.sell_price if service.price is None else service.price
                info["final_price"] = info["base_price"]

                hasPromotion = await self.uow.promotions.get_by_object(materialObj.id, "material")
                if hasPromotion is not None:
                    info["promotion_id"] = hasPromotion.id
                    if hasPromotion.promo_type == PromotionType.FIXED_AMOUNT and hasPromotion.discount_value:
                        discount = info["base_price"] - hasPromotion.discount_value
                        info["final_price"] = discount if discount >= 0 else 0
                    elif hasPromotion.promo_type == PromotionType.PERCENTAGE and hasPromotion.discount_value:
                        discount = info["base_price"] * (hasPromotion.discount_value / 100)
                        info["final_price"] = info["base_price"] - discount

            price_info.append(info)

        await self.uow.appointmentRecords.create(data, price_info)
        return await self.uow.appointments.get(data.appointment_id)
    
    async def get(self, id: int) -> AppointmentRecords:
        result = await self.uow.appointmentRecords.get(id)
        if result is None: raise AppointmentRecordNotFound(id)
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
        if check is None: raise AppointmentRecordNotFound(id)

        receipts = await self.uow.db.scalars(
            select(Receipt)
            .options(raiseload("*"))
            .where(Receipt.appointment_id == check.appointment_id)
        )

        appointmentID = check.appointment_id

        if any(receipt.status != ReceiptStatus.CANCELLED for receipt in receipts):
            raise AppointmentHasActiveReceipts(appointmentID)
        
        await self.uow.appointmentRecords.delete(id)
        return await self.uow.appointments.get(appointmentID)
    