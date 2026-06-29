import math
from fastapi import HTTPException, status
from src.core.decorators.requireID import require_exists
from src.core.dependencies.uow import UnitOfWork
from src.repository.payroll.payroll_model import Payroll
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
        if payroll.payout_id: raise HTTPException(400, "Нельзя изменить выплаченную заработную плату / коммисию / бонусы, сначало отмените связанную выплату")

        dataDict = data.model_dump(exclude = {"id"}, exclude_unset = True)
        return await self.uow.payrolls.update(data, **dataDict)
    
    async def get(self, id: int) -> Payroll:
        result = await self.uow.payrolls.get(id)
        if not result:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = f"Payroll with id {id} not found"
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
    
    @require_exists("payrolls")
    async def delete(self, id: int) -> bool:
        return await self.uow.payrolls.delete(id)
    