from decimal import Decimal
from sqlalchemy import func, select
from src.database.base import BaseRepository
from src.repository.tenant.payments.tenantExpeses_model import TenantExpenses

class TenantExpensesRepository(BaseRepository[TenantExpenses]):
    async def create(self, expense: TenantExpenses) -> TenantExpenses:
        self.db.add(expense)
        await self.db.flush()
        await self.db.refresh(expense)
        return expense

    async def get_by_tenant(self, tenant_id: int) -> list[TenantExpenses]:
        result = await self.db.execute(
            select(TenantExpenses)
            .where(TenantExpenses.tenant_id == tenant_id)
            .order_by(TenantExpenses.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_category(self, tenant_id: int, category: str) -> list[TenantExpenses]:
        result = await self.db.execute(
            select(TenantExpenses)
            .where(
                TenantExpenses.tenant_id == tenant_id,
                TenantExpenses.category == category,
            )
            .order_by(TenantExpenses.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_total_spent(self, tenant_id: int) -> Decimal:
        result = await self.db.execute(
            select(func.coalesce(func.sum(TenantExpenses.amount), 0)).where(
                TenantExpenses.tenant_id == tenant_id
            )
        )
        return result.scalar_one()
