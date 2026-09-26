from sqlalchemy import select
from src.database.base import BaseRepository
from src.repository.globalClient.globalClient_model import GlobalClient

class GlobalClientRepository(BaseRepository[GlobalClient]):
    async def create(self, client: GlobalClient) -> GlobalClient:
        self.db.add(client)
        await self.db.flush()
        await self.db.refresh(client)
        return client

    async def get_by_telegram_user_id(self, telegram_user_id: int) -> GlobalClient | None:
        result = await self.db.execute(
            select(GlobalClient).where(GlobalClient.telegram_user_id == telegram_user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_telegram_phone(self, phone: str) -> GlobalClient | None:
        result = await self.db.execute(
            select(GlobalClient).where(GlobalClient.telegram_phone == phone)
        )
        return result.scalar_one_or_none()

    async def get_telegram_user_ids(self, ids: list[int]) -> dict[int, int]:
        """global client id -> telegram_user_id, for notifying clients."""
        if not ids: return {}
        result = await self.db.execute(
            select(GlobalClient.id, GlobalClient.telegram_user_id).where(GlobalClient.id.in_(ids))
        )
        return {row[0]: row[1] for row in result.all()}
