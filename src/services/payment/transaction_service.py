import math
from fastapi import HTTPException
from src.core.dependencies.uow import UnitOfWork
from src.schemas.base import RequestAllObject
from src.repository.transaction.transaction_model import Transaction
from src.schemas.transaction.create import TransactionCreateSchema
from src.schemas.transaction.update import TransactionUpdateSchema

class TransactionService():
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create(self, data: TransactionCreateSchema) -> Transaction:
        transactionData = data.model_dump()
        newTransaction = Transaction(**transactionData)
        return await self.uow.transactions.create(newTransaction)
    
    async def update(self, data: TransactionUpdateSchema) -> Transaction:
        dataDict = data.model_dump(exclude = {"id"}, exclude_unset = True)
        result = await self.uow.transactions.update(data.id, **dataDict)
        if result is None:
            raise HTTPException(
                status_code = 404,
                detail = f"Транзакции с ID {data.id} не найден"
            )
        return result
    
    async def get(self, id: int) -> Transaction:
        result = await self.uow.transactions.get(id)
        if result is None:
            raise HTTPException(
                status_code = 404,
                detail = f"Транзакции с ID {id} не найден"
            )
        return result
    
    async def get_many(self, ids: list[int]) -> list[Transaction]:
        return await self.uow.transactions.get_by_ids(ids)
    
    async def get_all(self, data: RequestAllObject) -> dict:
        items, total_items = await self.uow.transactions.get_all(data)

        total_pages = math.ceil(total_items / data.pageSize) if data.pageSize > 0 else 0
        
        return {
            "items": items,
            "page": data.page,
            "pageSize": data.pageSize,
            "totalItems": total_items,
            "totalPages": total_pages
        }
    
    async def cancel(self, id: int) -> Transaction:
        transaction = await self.uow.transactions.get(id)
        if transaction is None:
            raise HTTPException(404, f"Транзакции с ID {id} не найден")
        if transaction.auto_generated:
            raise HTTPException(400, "Нельзя отменять автоматически сгенерированные транзакции, отмените связанные счета.")
        return await self.uow.transactions.update(id, cancelled = True)
    