from sqlalchemy import func, select
from src.core.utils.model_filter import apply_dynamic_filters
from src.database.base import BaseRepository
from src.repository.transaction.transaction_model import Transaction
from src.schemas.base import RequestAllObject

class TransactionRepository(BaseRepository[Transaction]):
    async def create(self, transaction: Transaction) -> Transaction:
        self.db.add(transaction)
        await self.db.flush()
        await self.db.refresh(transaction)
        return (transaction)
    
    async def get(self, id: int) -> Transaction:
        return await self.db.get(Transaction, id)
    
    async def get_by_ids(self, ids: list[int]) -> list[Transaction]:
        result = await self.db.execute(
            select(Transaction).where(Transaction.id.in_(ids))
        )
        return list(result.scalars().all())
    
    async def get_all(self, data: RequestAllObject) -> tuple[list[Transaction], int]:
        count_stmt = select(func.count()).select_from(Transaction)
        stmt = select(Transaction)
        count_stmt = apply_dynamic_filters(count_stmt, Transaction, data.filters)
        stmt = apply_dynamic_filters(stmt, Transaction, data.filters)
        total_items = await self.db.scalar(count_stmt) or 0
        offset_value = (data.page - 1) * data.pageSize
        stmt = stmt.offset(offset_value).limit(data.pageSize)
        result = await self.db.execute(stmt)
        items = list(result.scalars().all())
        return items, total_items
    
    # async def update(self, payload: ServiceCategoryUpdateSchema) -> Transaction | None:
        # obj = await self.db.get(Transaction, payload.id)
        # if not obj:
        #     return None

        # obj.name = payload.name
        
        # await self.db.flush()
        # await self.db.refresh(obj)

        # return obj

    