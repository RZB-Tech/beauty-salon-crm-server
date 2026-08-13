from sqlalchemy import func, select
from src.core.utils.model_filter import apply_dynamic_filters
from src.database.base import BaseRepository
from src.repository.giftCard.giftCard_model import GiftCard
from src.schemas.base import RequestAllObject

class GiftCardRepository(BaseRepository[GiftCard]):
    async def create(self, giftCard: GiftCard):
        self.db.add(giftCard)
        await self.db.flush()
        await self.db.refresh(giftCard)
        return giftCard

    async def get_by_ids(self, ids: list[int]) -> list[GiftCard]:
        result = await self.db.execute(
            select(GiftCard).where(GiftCard.id.in_(ids))
        )
        return result.scalars().all()
    
    async def get_all(self, data: RequestAllObject) -> tuple[list[GiftCard], int]:
        count_stmt = select(func.count()).select_from(GiftCard)
        stmt = select(GiftCard)
        count_stmt = apply_dynamic_filters(count_stmt, GiftCard, data.filters)
        stmt = apply_dynamic_filters(stmt, GiftCard, data.filters)
        total_items = await self.db.scalar(count_stmt) or 0
        offset_value = (data.page - 1) * data.pageSize
        stmt = stmt.order_by(GiftCard.id.desc()).offset(offset_value).limit(data.pageSize)
        result = await self.db.execute(stmt)
        items = result.scalars().all()
        return items, total_items

    async def get_by_code(self, code: str) -> GiftCard | None:
        stmt = (
            select(GiftCard)
            .where(GiftCard.code == code)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()