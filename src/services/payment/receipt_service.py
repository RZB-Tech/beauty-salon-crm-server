import math
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from src.core.dependencies.uow import UnitOfWork
from src.repository.payment.payment_model import Payment, PaymentMethodsEnum, Receipt, ReceiptItem, ReceiptStatus, ReceiptType
from src.repository.payroll.payroll_model import Payroll, PayrollStatus, PayrollType
from src.schemas.base import RequestAllObject
from src.schemas.payment.create import ReceiptCreateSchema
from src.schemas.tenant.base import TenantPreferencesSchema
from src.core.utils.common import as_utc

class ReceiptService():
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create(self, data: ReceiptCreateSchema) -> Receipt:
        if data.appointment_id:
            active_stmt = (
                select(Receipt)
                    .where(
                        Receipt.appointment_id == data.appointment_id,
                        Receipt.status.in_([ReceiptStatus.PENDING, ReceiptStatus.PAID])
                    )
            )
            active_result = await self.uow.db.execute(active_stmt)
            existing_active_receipt = active_result.scalar_one_or_none()
            
            if existing_active_receipt:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Appointment {data.appointment_id} already has an active bill "
                        f"(Receipt #{existing_active_receipt.id} is {existing_active_receipt.status}). "
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
                    detail="Для прямой продажи необходимо указать список из одного и более товаров"
                )
            
            runningTotal = 0
            
            for item_data in data.receipt_items:
                material = await self.uow.materials.get(item_data.material_id)
                if not material:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, 
                        detail=f"Материал с ID {item_data.material_id} не найден."
                    )
                if material.archived:
                    raise HTTPException(409, f"Нельзя использовать архивированный Товар {material.name}, ID {material.id}")
                if material.quantity < item_data.quantity:
                    raise HTTPException(
                        status_code= 400, 
                        detail=f"Не достаточное количество материала ID {material.id}, {material.article}. Доступо: {material.quantity}, запрашивается: {item_data.quantity}."
                    )
                
                newQuantity = material.quantity - item_data.quantity
                await self.uow.materials.update(material.id, newQuantity)
                
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
            raise HTTPException(404, detail = f"Чек с ID {id} не найден")
        
        if receipt.status == ReceiptStatus.CANCELLED:
            raise HTTPException(400, detail = f"Чек уже отменен")

        await self.ensure_receipt_payments_can_be_cancelled(receipt)
        
        deposit_to_refund = 0
        for payment in receipt.payments:
            if payment.method == PaymentMethodsEnum.DEPOSIT:
                deposit_to_refund += payment.amount
            await self.uow.payments.cancel(payment.id)

        if receipt.change_to_deposit and receipt.change_amount > 0:
            deposit_to_refund -= receipt.change_amount

        if deposit_to_refund != 0:
            client_id = receipt.appointment.client_id
            client = await self.uow.clients.get(client_id)
            if client:
                new_deposit_balance = client.deposit + deposit_to_refund
                await self.uow.clients.updateDeposit(client, new_deposit_balance)

        # cancel payments and payrolls
        if receipt:
            stmt = await self.uow.db.execute(
                select(Payroll)
                .where( 
                    Payroll.appointment_id == receipt.appointment_id,
                    Payroll.type == PayrollType.COMMISSION
                )
            )
            payrolls = stmt.scalars().all()
            # cancel payrolls
            for payroll in payrolls:
                payroll.status = PayrollStatus.CANCELLED

            # cancel payments
            for payment in receipt.payments:
                payment.cancelled = True

        # return used materials to stock
        if receipt.receipt_type == ReceiptType.DIRECT_SALE:
            for receiptItem in receipt.items:
                material = await self.uow.materials.get(receiptItem.material_id)
                if not material: continue
                newQuantity = material.quantity + receiptItem.quantity
                await self.uow.materials.update(material.id, newQuantity)

        receipt.status = ReceiptStatus.CANCELLED
        if receipt.appointment:
            receipt.appointment.paid = False

        receipt.change_amount = 0
        receipt.change_to_deposit = False

        # cancel all related transcations
        transactions = await self.uow.transactions.get_by_receipt(receipt.id)
        for transaction in transactions: transaction.cancelled = True
            
        return await self.uow.receipts.get(id)

    async def ensure_receipt_payments_can_be_cancelled(self, receipt: Receipt) -> None:
        if not receipt.payments:
            return

        preferences = await self.uow.tenantPreferences.get_by_tenant_id(receipt.tenant_id)
        preference_data = (
            preferences.preferences
            if preferences is not None
            else TenantPreferencesSchema().model_dump()
        )
        cancel_payment_due = TenantPreferencesSchema(**preference_data).cancel_payment_due

        expired_payment = next(
            (
                payment
                for payment in receipt.payments
                if self.is_payment_cancel_expired(payment, cancel_payment_due)
            ),
            None,
        )
        if expired_payment is None:
            return

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Время для отмены чека истекло: в чеке есть оплата, "
                f"которую можно отменить только в течение {cancel_payment_due} ч. после создания."
            ),
        )

    def is_payment_cancel_expired(self, payment: Payment, cancel_payment_due: int) -> bool:
        cancel_deadline = as_utc(payment.created_at) + timedelta(hours=cancel_payment_due)
        return datetime.now(timezone.utc) > cancel_deadline

    async def get(self, id: int) -> Receipt:
        result = await self.uow.receipts.get(id)
        if result is None: raise HTTPException(404)
        return result

    async def get_many(self, ids: list[int]) -> list[Receipt]:
        return await self.uow.receipts.get_by_ids(ids)
    
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
