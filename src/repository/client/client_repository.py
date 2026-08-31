from sqlalchemy import func, select
from src.database.base import BaseRepository
from src.schemas.base import RequestAllObject
from src.schemas.client.create import ClientCreateSchema
from src.repository.client.client_model import Client
from src.core.utils.model_filter import apply_dynamic_filters

class ClientRepository(BaseRepository[Client]):
    async def create(self, client: ClientCreateSchema) -> Client:
        self.db.add(client)
        await self.db.flush()
        await self.db.refresh(client)
        return client
        
    async def get_by_ids(self, ids: list[int]) -> list[Client]:
        result = await self.db.execute(
            select(Client).where(Client.id.in_(ids))
        )
        return result.scalars().all()
    
    async def get_all(self, data: RequestAllObject) -> tuple[list[Client], int]:
        count_stmt = select(func.count()).select_from(Client)
        stmt = select(Client)
        count_stmt = apply_dynamic_filters(count_stmt, Client, data.filters)
        stmt = apply_dynamic_filters(stmt, Client, data.filters)
        total_items = await self.db.scalar(count_stmt) or 0
        offset_value = (data.page - 1) * data.pageSize
        stmt = stmt.order_by(Client.id.desc()).offset(offset_value).limit(data.pageSize)
        result = await self.db.execute(stmt)
        items = result.scalars().all()
        return items, total_items 