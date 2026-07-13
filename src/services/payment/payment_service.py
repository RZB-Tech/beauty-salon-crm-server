import math
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from src.core.dependencies.uow import UnitOfWork
from src.repository.appointment.appointment_model import AppointmentServices
from src.repository.payment.payment_model import Payment, PaymentMethodsEnum, Receipt, ReceiptItem, ReceiptStatus, ReceiptType
from src.repository.payroll.payroll_model import Payroll, PayrollType
from src.repository.transaction.transaction_model import Transaction, TransactionCategory, TransactionMethod, TransactionType
from src.schemas.base import RequestAllObject
from src.schemas.payment.create import PaymentCreateSchema
from src.schemas.tenant.base import TenantPreferencesSchema
from src.core.utils.common import as_utc

class PaymentService():
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create(self, data: PaymentCreateSchema) -> Receipt: 
        stmt = await self.uow.db.execute(select(Receipt)
            .where(Receipt.id == data.receipt_id)
            .options(
                selectinload(Receipt.payments),
                selectinload(Receipt.appointment),
                selectinload(Receipt.items)
                    .selectinload(ReceiptItem.appointment_service)
                    .selectinload(AppointmentServices.appointment_record)
            ))
        
        # get receipt info
        receipt = stmt.scalar_one_or_none()
        if not receipt:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Receipt with id {data.receipt_id} not found"
            )
            
        # check if receipt is already paid
        current_paid = sum(p.amount for p in receipt.payments)
        if current_paid >= receipt.total_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This receipt has already been fully paid. No further payments accepted."
            )
        
        # create temp deposit adjustment to substract payment sum in case if payment method is deposit
        depositAdjustment = 0
        if data.method == PaymentMethodsEnum.DEPOSIT:
            depositAdjustment -= data.amount

        new_payment = Payment(amount = data.amount, method = data.method)
        receipt = await self.uow.payments.create(data.receipt_id, new_payment)

        # add overpaid sum to client's deposit
        if receipt.paid_amount >= receipt.total_amount:
            receipt.status = ReceiptStatus.PAID

            # create new transcation for income from receipt payment
            await self.uow.transactions.create(Transaction(
                receipt_id = receipt.id,
                amount = receipt.total_amount,
                type = TransactionType.INCOME,
                method = TransactionMethod(new_payment.method),
                category = TransactionCategory.RECEIPT,
                auto_generated = True
            ))

            if receipt.appointment:
                receipt.appointment.paid = True
            
            overpayment = receipt.paid_amount - receipt.total_amount
            if overpayment > 0:
                if not data.add_change_to_deposit: raise HTTPException(400, "Переплата, измените сумму или оплатите с учетом перевода сдачи в депозит клиента")
                receipt.change_amount = overpayment
                receipt.change_to_deposit = data.add_change_to_deposit
                
                if data.add_change_to_deposit:
                    depositAdjustment += overpayment

                # create new transaction for deposit
                await self.uow.transactions.create(Transaction(
                    receipt_id = receipt.id,
                    amount = overpayment,
                    type = TransactionType.INCOME,
                    method = TransactionMethod.DEPOSIT,
                    category = TransactionCategory.RECEIPT,
                    auto_generated = True
                ))

            # add commission to employees
            if receipt.receipt_type == ReceiptType.APPOINTMENT:
                for item in receipt.items:
                    if not item.appointment_service_id:
                        continue
                        
                    appointment_service = item.appointment_service
                    appointment_record = appointment_service.appointment_record
                    employee_id = appointment_record.employee_id
                    
                    employee = await self.uow.employees.get(employee_id)
                    if not employee:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Employee with id {employee.id} not found."
                        )
                    
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
                method = TransactionMethod(new_payment.method),
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

            if not client:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"During payment client with id {client_id} not found"
                )

            if data.method == PaymentMethodsEnum.DEPOSIT and data.amount > client.deposit:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Client does not have enough deposit to make payment."
                )
            
            final_deposit_balance = client.deposit + depositAdjustment
            await self.uow.clients.update(client.id, deposit = final_deposit_balance)

        return await self.uow.receipts.get(receipt.id)
    
    async def get(self, id: int) -> Payment:
        result = await self.uow.payments.get(id)
        if result is None:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"Оплата с ID {id} не найден"
            )
        return result
    
    async def get_many(self, ids: list[int]) -> list[Payment]:
        return await self.uow.payments.get_by_ids(ids)
    
    async def get_all(self, data: RequestAllObject) -> dict:
        items, total_items = await self.uow.payments.get_all(data)

        total_pages = math.ceil(total_items / data.pageSize) if data.pageSize > 0 else 0
        
        return {
            "items": items,
            "page": data.page,
            "pageSize": data.pageSize,
            "totalItems": total_items,
            "totalPages": total_pages
        }
    
    async def cancel(self, id: int) -> Payment:
        payment = await self.get(id)
        await self.ensure_payment_can_be_cancelled(payment)

        result = await self.uow.payments.update(id, cancelled = True)
        return result

    async def ensure_payment_can_be_cancelled(self, payment: Payment) -> None:
        preferences = await self.uow.tenantPreferences.get_by_tenant_id(payment.tenant_id)
        preference_data = (
            preferences.preferences
            if preferences is not None
            else TenantPreferencesSchema().model_dump()
        )
        cancel_payment_due = TenantPreferencesSchema(**preference_data).cancel_payment_due
        cancel_deadline = as_utc(payment.created_at) + timedelta(hours=cancel_payment_due)

        if datetime.now(timezone.utc) > cancel_deadline:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Время для отмены оплаты истекло. "
                    f"Отменить оплату можно только в течение {cancel_payment_due} ч. после создания."
                ),
            )
