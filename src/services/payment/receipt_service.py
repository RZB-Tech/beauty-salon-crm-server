import math
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from src.core.dependencies.uow import UnitOfWork
from src.exceptions.appointment_exceptions import AppointmentHasActiveReceipts, AppointmentNotFound
from src.exceptions.base import BaseAppException
from src.exceptions.client_exceptions import ClientNotFound, DepositNotEnough
from src.exceptions.employee_exceptions import EmployeeNotFound
from src.exceptions.general_exceptions import ObjectIsArchived, PaymentCancelDueExpired
from src.exceptions.material_exceptions import MaterialAmountInsufficient, MaterialArchived, MaterialNotFound
from src.exceptions.receipt_exceptions import ReceiptIsCancelled, ReceiptIsPaid, ReceiptNotFound, ReceiptOverpayment, ReceiptWithEmptyAppointmentRecords
from src.repository.appointment.appointment_model import AppointmentServices
from src.repository.receipt.receipt_model import Receipt, ReceiptItem, ReceiptStatus, ReceiptType
from src.repository.payroll.payroll_model import Payroll, PayrollStatus, PayrollType
from src.repository.transaction.transaction_model import Transaction, TransactionCategory, TransactionMethod, TransactionType
from src.schemas.base import RequestAllObject
from src.schemas.payment.create import ReceiptCreateSchema, ReceiptPaymentCreateSchema
from src.schemas.tenant.base import TenantPreferencesSchema
from src.services.system.tenantPreferences_service import TenantPreferencesService
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
            
            if existing_active_receipt: raise AppointmentHasActiveReceipts(data.appointment_id)

        newReceipt = Receipt(
            receipt_type = data.receipt_type,
            client_id = data.client_id
        )

        if data.receipt_type == ReceiptType.APPOINTMENT:
            appointment = await self.uow.appointments.get(data.appointment_id)
            if appointment is None: raise AppointmentNotFound(data.appointment_id)

            if len(appointment.records) == 0: raise ReceiptWithEmptyAppointmentRecords(data.appointment_id)

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
            runningTotal = 0
            
            for item_data in data.receipt_items:
                material = await self.uow.materials.get(item_data.material_id)
                if material is None: raise MaterialNotFound(item_data.material_id)

                if material.archived: raise ObjectIsArchived(material.id, "materials")
                if material.quantity < item_data.quantity: raise MaterialAmountInsufficient(material.id, material.name, item_data.quantity, material.quantity)
                
                newQuantity = material.quantity - item_data.quantity
                await self.uow.materials.update(material.id, quantity = newQuantity)
                
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
                raise BaseAppException(
                    detail = "Conflict, for this appointment active receipt was created in parallel",
                    errroCode = "RECEIPT_CREATION_CONFLICT",
                    statusCode = 500
                )

            # If it's a different database error (like a bad check constraint), bubble up the real truth
            raise BaseAppException(
                detail = f"Database integrity violance: {error_msg}",
                errorCode = "DATABASE_INTEGRITY_VIOLANCE",
                statudCode = 500,
                error = error_msg
            )
    
    async def make_payment(self, data: ReceiptPaymentCreateSchema) -> Receipt:
        stmt = await self.uow.db.execute(select(Receipt)
            .where(Receipt.id == data.receipt_id)
            .options(
                selectinload(Receipt.transactions),
                selectinload(Receipt.appointment),
                selectinload(Receipt.items)
                    .selectinload(ReceiptItem.appointment_service)
                    .selectinload(AppointmentServices.appointment_record)
            ))
        
        # get receipt info
        receipt = stmt.scalar_one_or_none()
        if not receipt: raise ReceiptNotFound(data.receipt_id)

        if receipt.status == ReceiptStatus.CANCELLED: raise ReceiptIsCancelled(data.receipt_id)
            
        # check if receipt is already paid
        if receipt.remaining_amount == 0: raise ReceiptIsPaid(data.receipt_id)
        
        # create temp deposit adjustment to substract payment sum in case if payment method is deposit
        depositAdjustment = 0
        if data.method == TransactionMethod.DEPOSIT:
            depositAdjustment -= data.amount

        # add overpaid sum to client's deposit
        if receipt.paid_amount + data.amount >= receipt.total_amount:
            receipt.status = ReceiptStatus.PAID

            overpayment = (receipt.paid_amount + data.amount) - receipt.total_amount
            applied_amount = data.amount - overpayment

            # create new transcation for income from receipt payment
            await self.uow.transactions.create(Transaction(
                receipt_id = receipt.id,
                amount = applied_amount,
                type = TransactionType.INCOME,
                method = TransactionMethod(data.method),
                category = TransactionCategory.RECEIPT,
                auto_generated = True
            ))

            if receipt.appointment:
                receipt.appointment.paid = True

            if overpayment > 0:
                if not data.add_change_to_deposit: raise ReceiptOverpayment()
                receipt.change_amount = overpayment
                receipt.change_to_deposit = True
                
                if data.add_change_to_deposit: depositAdjustment += overpayment
                
            # add commission to employees
            if receipt.receipt_type == ReceiptType.APPOINTMENT:
                for item in receipt.items:
                    if not item.appointment_service_id:
                        continue
                        
                    appointment_service = item.appointment_service
                    appointment_record = appointment_service.appointment_record
                    employee_id = appointment_record.employee_id
                    
                    employee = await self.uow.employees.get(employee_id)
                    if employee is None: raise EmployeeNotFound(employee_id)
                    
                    if employee and employee.percent_from_services > 0:
                        commission_earned = int(item.subtotal * (employee.percent_from_services / 100))
                        if commission_earned > 0:
                            payroll_record = Payroll(
                                employee_id = employee.id,
                                appointment_id = appointment_record.appointment_id,
                                type = PayrollType.COMMISSION,
                                amount = commission_earned,
                                auto_generated = True
                            )
                            await self.uow.payrolls.create(payroll_record)
        else:
            receipt.change_amount = 0
            receipt.change_to_deposit = False

            await self.uow.transactions.create(Transaction(
                receipt_id = receipt.id,
                amount = data.amount,
                type = TransactionType.INCOME,
                method = TransactionMethod(data.method),
                category = TransactionCategory.RECEIPT,
                auto_generated = True
            ))

        # substract payment sum from client's deposit
        if depositAdjustment != 0:
            client_id: int
            client_id = (receipt.appointment.client_id
                         if receipt.appointment_id
                         else receipt.client_id)
            client = await self.uow.clients.get(client_id)

            if client is None: raise ClientNotFound(client_id)

            if data.method == TransactionMethod.DEPOSIT and data.amount > client.deposit:
                raise DepositNotEnough(client.id, client.firstname, data.amount, client.deposit)
            
            final_deposit_balance = client.deposit + depositAdjustment
            await self.uow.clients.update(client.id, deposit = final_deposit_balance)
            await self.uow.transactions.create(Transaction(
                    receipt_id = receipt.id,
                    amount = data.amount,
                    type = TransactionType.INCOME,
                    method = TransactionMethod.DEPOSIT,
                    category = TransactionCategory.RECEIPT,
                    auto_generated = True
                ))

        return await self.uow.receipts.get(receipt.id)

    async def cancel(self, id: int) -> Receipt:
        receipt = await self.uow.receipts.get(id)
        if receipt is None: raise ReceiptNotFound(id)
        
        if receipt.status == ReceiptStatus.CANCELLED:
            raise ReceiptIsCancelled(id)

        await self.ensure_receipt_payments_can_be_cancelled(receipt)
        
        deposit_to_refund = 0
        for transaction in receipt.transactions: 
            if transaction.method == TransactionMethod.DEPOSIT: 
                deposit_to_refund += transaction.amount

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

        # return used materials to stock
        if receipt.receipt_type == ReceiptType.DIRECT_SALE:
            for receiptItem in receipt.items:
                material = await self.uow.materials.get(receiptItem.material_id)
                if not material: continue
                newQuantity = material.quantity + receiptItem.quantity
                await self.uow.materials.update(material.id, quantity = newQuantity)

        receipt.status = ReceiptStatus.CANCELLED
        if receipt.appointment:
            receipt.appointment.paid = False

        receipt.change_amount = 0
        receipt.change_to_deposit = False

        for transaction in receipt.transactions: transaction.cancelled = True
            
        return await self.uow.receipts.get(id)

    async def ensure_receipt_payments_can_be_cancelled(self, receipt: Receipt) -> None:
        if not receipt.transactions:
            return

        tenant = await TenantPreferencesService.get_tenant_or_raise(self)
        preferences = TenantPreferencesSchema(**tenant.preferences).model_dump()
        cancel_payment_due = preferences["cancel_payment_due"]

        expired_payment = next(
            (
                transaction
                for transaction in receipt.transactions
                if self.is_payment_cancel_expired(transaction, cancel_payment_due)
            ),
            None,
        )
        if expired_payment is None:
            return

        raise PaymentCancelDueExpired(cancel_payment_due)

    def is_payment_cancel_expired(self, payment: Transaction, cancel_payment_due: int) -> bool:
        cancel_deadline = as_utc(payment.created_at) + timedelta(hours=cancel_payment_due)
        return datetime.now(timezone.utc) > cancel_deadline

    async def get(self, id: int) -> Receipt:
        result = await self.uow.receipts.get(id)
        if result is None: raise ReceiptNotFound(id)
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
