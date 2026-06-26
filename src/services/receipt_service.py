import math
from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from src.core.decorators.requireID import require_exists
from src.core.dependencies.uow import UnitOfWork
from src.repository.appointment.appointment_model import AppointmentStatus
from src.repository.payment.payment_model import PaymentMethodsEnum, Receipt, ReceiptItem, ReceiptStatusEnum, ReceiptType
from src.repository.payroll.payroll_model import Payroll, PayrollEnum
from src.schemas.base import RequestAllObject
from src.schemas.payment.create import ReceiptCreateSchema

class ReceiptService():
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create(self, data: ReceiptCreateSchema) -> Receipt:
        if data.appointment_id:
            active_stmt = (
                select(Receipt)
                    .where(
                        Receipt.appointment_id == data.appointment_id,
                        Receipt.status.in_([ReceiptStatusEnum.PENDING, ReceiptStatusEnum.PAID])
                    )
            )
            active_result = await self.uow.db.execute(active_stmt)
            existing_active_receipt = active_result.scalar_one_or_none()
            
            if existing_active_receipt:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Appointment {data.appointment_id} already has an active bill "
                        f"(Receipt #{existing_active_receipt.id} is {existing_active_receipt.status.value}). "
                        f"Cancel it before issuing a new one."
                    )
                )

        newReceipt = Receipt(
            receipt_type = data.receipt_type,
            client_id = data.client_id
        )

        if data.receipt_type == ReceiptType.APPOINTMENT:
            if not data.appointment_id:
                raise HTTPException(
                    status_code= 400, 
                    detail="appointment_id is required for APPOINTMENT receipt type."
                )
            
            if data.client_id:
                raise HTTPException(
                    status_code = 400, 
                    detail="Client cannot be provided when appointment provided"
                )
            
            appointment = await self.uow.appointments.get(data.appointment_id)
            if not appointment:
                raise HTTPException(
                    status_code= 404, 
                    detail=f"Appointment with id {data.appointment_id} not found"
                )
            
            if len(appointment.records) == 0:
                raise HTTPException(
                    status_code= 400, 
                    detail=f"Cannot createt receipt for appointment which does not have records"
                )

            newReceipt.appointment_id = appointment.id
            runningTotal = 0

            for record in appointment.records:
                for service in record.services:
                    item = ReceiptItem(
                        appointment_service_id = service.id,
                        price = service.price,
                        quantity = service.quantity
                    )
                    runningTotal += (service.price * service.quantity)
                    newReceipt.items.append(item)
            
            newReceipt.total_amount = runningTotal

        else:
            if not data.receipt_items:
                raise HTTPException(
                    status_code= 400, 
                    detail="Items list is required for direct sales."
                )
            
            runningTotal = 0
            
            for item_data in data.receipt_items:
                material = await self.uow.materials.get(item_data.material_id)
                if not material:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, 
                        detail=f"Material with ID {item_data.material_id} not found."
                    )
                if material.quantity < item_data.quantity:
                    raise HTTPException(
                        status_code= 400, 
                        detail=f"Not enough stock for material {material.id}. Available: {material.quantity}, Requested: {item_data.quantity}."
                    )
                
                newQuantity = material.quantity - item_data.quantity
                await self.uow.materials.updateQuantity(material, newQuantity)
                
                item_price = material.sell_price
                runningTotal += item_price * item_data.quantity
                
                receipt_item = ReceiptItem(
                    material_id=item_data.material_id,
                    price=item_price,
                    quantity=item_data.quantity
                )
                
                newReceipt.items.append(receipt_item)
            
            newReceipt.total_amount = runningTotal

        try:
            return await self.uow.receipts.create(newReceipt)
        except IntegrityError as exc:
            error_msg = str(exc.orig)
            
            # Check if our specific unique index name is in the Postgres error string
            if "idx_unique_active_receipt_per_appointment" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Concurrency conflict: An active receipt was just generated for this appointment elsewhere."
                )
            
            # If it's a different database error (like a bad check constraint), bubble up the real truth
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database integrity violation: {error_msg}"
            )
    
    async def cancel(self, id: int) -> Receipt:
        receipt = await self.uow.receipts.get(id)
        if not receipt:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"Receipt with id {id} not found"
            )
        
        if receipt.status == ReceiptStatusEnum.CANCELLED:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = f"Receipt has already cancelled"
            )
        
        deposit_to_refund = 0
        for payment in receipt.payments:
            if payment.method == PaymentMethodsEnum.DEPOSIT:
                deposit_to_refund += payment.amount

        if receipt.change_to_deposit and receipt.change_amount > 0:
            deposit_to_refund -= receipt.change_amount

        if deposit_to_refund != 0:
            client_id = receipt.appointment.client_id
            client = await self.uow.clients.get(client_id)
            if client:
                new_deposit_balance = client.deposit + deposit_to_refund
                await self.uow.clients.updateDeposit(client, new_deposit_balance)

        if receipt.appointment_id:
            payroll_delete_stmt = (
                delete(Payroll)
                .where( 
                    Payroll.appointment_id == receipt.appointment_id,
                    Payroll.type == PayrollEnum.COMMISSION
                )
            )
            await self.uow.db.execute(payroll_delete_stmt)

        if receipt.receipt_type == ReceiptType.DIRECT:
            for receiptItem in receipt.items:
                material = await self.uow.materials.get(receiptItem.material_id)
                if not material: continue
                newQuantity = material.quantity + receiptItem.quantity
                await self.uow.materials.updateQuantity(material, newQuantity)

        receipt.status = ReceiptStatusEnum.CANCELLED
        if receipt.appointment:
            receipt.appointment.paid = False

        receipt.change_amount = 0
        receipt.change_to_deposit = False

        return await self.uow.receipts.get(id)
    
    # @require_exists("materials")
    # async def update(self, data: MaterialUpdateSchema) -> Material:
    #     return await self.uow.materials.update(data)
    
    # async def get(self, id: int) -> Material:
    #     result = await self.uow.materials.get(id)
    #     if not result:
    #         raise HTTPException(
    #             status_code = status.HTTP_404_NOT_FOUND,
    #             detail = f"Material with id {id} not found"
    #         )
    #     return result
    
    # async def get_many(self, ids: list[int]) -> list[Material]:
    #     return await self.uow.materials.get_by_ids(ids)
    
    async def get_all(self, data: RequestAllObject) -> dict:
        items, total_items = await self.uow.receipts.get_all(data)

        total_pages = math.ceil(total_items / data.pageSize) if data.pageSize > 0 else 0
        
        return {
            "items": items,
            "page": data.page,
            "pageSize": data.pageSize,
            "totalItems": total_items,
            "totalPages": total_pages
        }
    
    # @require_exists("materials")
    # async def delete(self, id: int) -> bool:
    #     return await self.uow.materials.delete(id)