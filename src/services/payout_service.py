import math
from fastapi import HTTPException, status
from src.core.decorators.requireID import require_exists
from src.core.dependencies.uow import UnitOfWork
from src.repository.payroll.payroll_model import Payout, PayrollStatus
from src.repository.transaction.transaction_model import Transaction, TransactionCategory, TransactionMethod, TransactionType
from src.schemas.base import RequestAllObject
from src.schemas.payout.create import PayoutCreateSchema

class PayoutService():
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
    
    @require_exists("employees", target_param = "employee_id")
    async def create(self, data: PayoutCreateSchema) -> Payout:
        payoutData = data.model_dump(exclude = {"payrolls", "start_date", "end_date"})
        payrollsIDs = data.payrolls or []

        validPayrolls = []

        if payrollsIDs:
            validPayrolls = await self.uow.payrolls.get_by_ids(payrollsIDs)
            if len(validPayrolls) != len(payrollsIDs):
                raise HTTPException(
                    status_code = 400,
                    detail = "Одно или более указанных выплат не найдена"
                )
            
            for payroll in validPayrolls:
                if payroll.employee_id != data.employee_id:
                    raise HTTPException(
                        status_code = 400,
                        detail = f"Выплата {payroll.id} не принадлежит указанному сотруднику"
                    )
                
                if payroll.status != PayrollStatus.PAID:
                    raise HTTPException(
                        status_code = 400,
                        detail  = f"Выплата {payroll.id} уже оплачена"
                    )
                
                if payroll.status != PayrollStatus.CANCELLED:
                    raise HTTPException(
                        status_code = 400,
                        detail  = f"Нельзя выплатить по выплате ID {payroll.id}"
                    )
        elif data.start_date and data.end_date:
            validPayrolls = await self.uow.payrolls.get_pendings(data.employee_id, data.start_date, data.end_date)
            if not validPayrolls: raise HTTPException(404, "У сотрудника в выбранном периоде нету не выплаченных компинсация / бонусов / штрафов")
        else:
            validPayrolls = await self.uow.payrolls.get_pendings(data.employee_id)
            if not validPayrolls: raise HTTPException(400, "У сотрудника в выбранном периоде нету не выплаченных компинсация / бонусов / штрафов")

        for payroll in validPayrolls:
            payroll.status = PayrollStatus.PAID

        newPayout = Payout(**payoutData)
        newPayout.payrolls = validPayrolls
        await self.uow.payouts.create(newPayout)
        result = await self.uow.payouts.get(newPayout.id)

        await self.uow.transactions.create(Transaction(
            amount = result.total_amount,
            type = TransactionType.EXPENSE,
            method = TransactionMethod(newPayout.method.value),
            category = TransactionCategory.EMPLOYEE_PAYMENT,
            payout_id = result.id,
            auto_generated = True
        ))

        return result

    # @require_exists("payrolls")
    # async def update(self, data: PayrollUpdateSchema) -> PaPayoutyroll:
    #     return await self.uow.payrolls.update(data)
    
    async def get(self, id: int) -> Payout:
        result = await self.uow.payoutss.get(id)
        if not result:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"Payout with id {id} not found"
            )
        return result
    
    async def get_many(self, ids: list[int]) -> list[Payout]:
        return await self.uow.payoutss.get_by_ids(ids)
    
    async def get_all(self, data: RequestAllObject) -> dict:
        items, total_items = await self.uow.payouts.get_all(data)

        total_pages = math.ceil(total_items / data.pageSize) if data.pageSize > 0 else 0
        
        return {
            "items": items,
            "page": data.page,
            "pageSize": data.pageSize,
            "totalItems": total_items,
            "totalPages": total_pages
        }
    