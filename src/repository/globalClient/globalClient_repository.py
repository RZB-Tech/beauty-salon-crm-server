from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from src.database.base import BaseRepository
from src.repository.globalClient.globalClient_model import GlobalClient

class GlobalClientRepository(BaseRepository[GlobalClient]):
    async def get_or_create_by_telegram(self, telegram_user_id: int, firstname: str,
                                        lastname: str | None, username: str | None) -> GlobalClient:
        # ON CONFLICT: the mini app fires several requests at once on first open
        await self.db.execute(
            insert(GlobalClient)
            .values(telegram_user_id = telegram_user_id, firstname = firstname,
                    lastname = lastname, telegram_username = username)
            .on_conflict_do_nothing(index_elements = [GlobalClient.telegram_user_id])
            # Not tenant-scoped; the tenant filter can't inspect core INSERT statements
            .execution_options(skip_tenant_filter = True)
        )
        result = await self.db.execute(
            select(GlobalClient).where(GlobalClient.telegram_user_id == telegram_user_id)
        )
        return result.scalar_one()

    async def get_by_contact_phone(self, phone: str) -> GlobalClient | None:
        result = await self.db.execute(
            select(GlobalClient).where(GlobalClient.contact_phone == phone)
        )
        return result.scalar_one_or_none()
