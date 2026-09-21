from decimal import Decimal

from sqlalchemy import func, select

from src.database.base import BaseRepository
from src.repository.tenant.tenant_model import TenantPayments

class TenantPaymentsRepository(BaseRepository[TenantPayments]):
    async def create(self, payment: TenantPayments) -> TenantPayments:
        self.db.add(payment)
        await self.db.flush()
        await self.db.refresh(payment)
        return payment

    async def get_by_tenant(self, tenant_id: int) -> list[TenantPayments]:
        result = await self.db.execute(
            select(TenantPayments)
            .where(TenantPayments.tenant_id == tenant_id)
            .order_by(TenantPayments.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_gateway_transaction(self, gateway: str, gateway_transaction_id: str) -> TenantPayments | None:
        result = await self.db.execute(
            select(TenantPayments).where(
                TenantPayments.gateway == gateway,
                TenantPayments.gateway_transaction_id == gateway_transaction_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_total_paid(self, tenant_id: int) -> Decimal:
        result = await self.db.execute(
            select(func.coalesce(func.sum(TenantPayments.amount), 0)).where(
                TenantPayments.tenant_id == tenant_id
            )
        )
        return result.scalar_one()
