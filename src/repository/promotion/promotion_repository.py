from sqlalchemy import func, select
from src.core.utils.model_filter import apply_dynamic_filters
from src.database.base import BaseRepository
from src.repository.promotion.promotion_model import Promotion
from src.schemas.base import RequestAllObject
from src.schemas.promotion.create import PromotionCreateSchema

class PromotionRepository(BaseRepository[Promotion]):

    async def create(self, promotion: PromotionCreateSchema) -> Promotion:
        self.db.add(promotion)
        await self.db.flush()
        await self.db.refresh(promotion)
        return promotion
    
    async def get_by_ids(self, ids: list[int]) -> list[Promotion]:
        result = await self.db.execute(
            select(Promotion).where(Promotion.id.in_(ids))
        )
        return result.scalars().all()
    
    async def get_all(self, data: RequestAllObject) -> tuple[list[Promotion], int]:
        count_stmt = select(func.count()).select_from(Promotion)
        stmt = select(Promotion)
        count_stmt = apply_dynamic_filters(count_stmt, Promotion, data.filters)
        stmt = apply_dynamic_filters(stmt, Promotion, data.filters)
        total_items = await self.db.scalar(count_stmt) or 0
        offset_value = (data.page - 1) * data.pageSize
        stmt = stmt.order_by(Promotion.id.desc()).offset(offset_value).limit(data.pageSize)
        result = await self.db.execute(stmt)
        items = result.scalars().all()
        return items, total_items