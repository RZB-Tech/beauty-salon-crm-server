from sqlalchemy import select
from src.database.base import BaseRepository
from src.repository.tenant.subscription.subscriptionPlan_model import AddonProduct

class AddonProductRepository(BaseRepository[AddonProduct]):
    async def get_all_available(self) -> list[AddonProduct]:
        """Products tenants can buy - archived ones are retired."""
        stmt = (
            select(AddonProduct)
            .where(AddonProduct.archived.is_(False))
            .order_by(AddonProduct.limit_key, AddonProduct.price)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
