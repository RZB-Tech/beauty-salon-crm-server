import math
from fastapi import HTTPException, status
from src.core.decorators.requireID import require_exists
from src.core.dependencies.uow import UnitOfWork
from src.repository.payroll.payroll_model import Payroll, PayrollStatus
from src.schemas.base import RequestAllObject
from src.schemas.payroll.create import PayrollCreateSchema
from src.schemas.payroll.update import PayrollUpdateSchema

class PayrollService():
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
    
    @require_exists("employees", target_param = "employee_id")
    async def create(self, data: PayrollCreateSchema) -> Payroll:
        payrollData = data.model_dump()
        newObject = Payroll(**payrollData)
        return await self.uow.payrolls.create(newObject)
    
    async def update(self, data: PayrollUpdateSchema) -> Payroll:
        payroll = await self.uow.payrolls.get(data.id)
        if payroll is None: raise HTTPException(404, f"Выплата с ID {data.id} не найден")
        if payroll.auto_genereted: raise HTTPException(400, "Нельзя изменить автоматически сгенерированную выплату, для этого внести изменения в сам Чек / Посещение")
        if payroll.payout_id: raise HTTPException(400, "Нельзя изменить выплаченную заработную плату / комиссию / бонусы, сначала отмените связанную выплату")
        if payroll.archived: raise HTTPException(400, f"Нельзя изменить архивированный объект")

        dataDict = data.model_dump(exclude = {"id"}, exclude_unset = True)

        result = await self.uow.payrolls.update(data.id, **dataDict)
        if not result:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"Выплата с ID {data.id} не найден"
            )
        return result
    
    async def get(self, id: int) -> Payroll:
        result = await self.uow.payrolls.get(id)
        if not result:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"Выплата с ID {id} не найден"
            )
        return result
    
    async def get_many(self, ids: list[int]) -> list[Payroll]:
        return await self.uow.payrolls.get_by_ids(ids)
    
    async def get_all(self, data: RequestAllObject) -> dict:
        items, total_items = await self.uow.payrolls.get_all(data)

        total_pages = math.ceil(total_items / data.pageSize) if data.pageSize > 0 else 0
        
        return {
            "items": items,
            "page": data.page,
            "pageSize": data.pageSize,
            "totalItems": total_items,
            "totalPages": total_pages
        }
    
    async def delete(self, id: int):
        payroll = await self.uow.payrolls.get(id)
        if payroll is None: raise HTTPException(404)
        if payroll.auto_genereted: raise HTTPException(409, "Нельзя удалять автоматически сгенерированные выплаты, для этого отмените связанный Чек")
        if payroll.payout_id: raise HTTPException(400, "Сначала отмените выплаченную сумму")
        if not payroll.archived: raise HTTPException(400, "Сначала нужно архивировать объект")

        await self.uow.payrolls.delete(id)

    async def cancel(self, id: int) -> Payroll:
        payroll = await self.uow.payrolls.get(id)
        if payroll is None: raise HTTPException(404)
        if payroll.status == PayrollStatus.CANCELLED: raise HTTPException(400, "Выплата уже отменена")
        if payroll.auto_genereted: raise HTTPException(409, "Нельзя отменить автоматически сгенерированную выплату. Требуется отменить связанные с ним Чек")
        if payroll.payout_id: raise HTTPException(409, "Сначала отмените выплаченную сумму")
        if payroll.archived: raise HTTPException(409, "Нельзя отменять архивированный объект")

        result = await self.uow.payrolls.update(id, status = PayrollStatus.CANCELLED)
        if result is None: raise HTTPException(404)
        return result