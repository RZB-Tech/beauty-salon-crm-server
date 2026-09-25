from datetime import datetime
from decimal import Decimal
from sqlalchemy import func, select
from src.database.base import BaseRepository
from src.repository.tenant.payments.tenantPayments_model import TenantPayments, TenantPaymentStatus

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

    async def get_by_gateway_transaction(
        self, gateway: str, gateway_transaction_id: str, lock: bool = False
    ) -> TenantPayments | None:
        stmt = select(TenantPayments).where(
            TenantPayments.gateway == gateway,
            TenantPayments.gateway_transaction_id == gateway_transaction_id,
        )
        if lock: stmt = stmt.with_for_update().execution_options(populate_existing = True)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_recent_pending_by_amount(self, gateway: str, amount: Decimal, since: datetime) -> list[TenantPayments]:
        """PENDING payments for `gateway` with exactly `amount`, created after `since`, newest first."""
        result = await self.db.execute(
            select(TenantPayments)
            .where(
                TenantPayments.gateway == gateway,
                TenantPayments.status == TenantPaymentStatus.PENDING,
                TenantPayments.amount == amount,
                TenantPayments.created_at > since,
            )
            .order_by(TenantPayments.id.desc())
        )
        return list(result.scalars().all())

    async def get_total_paid(self, tenant_id: int) -> Decimal:
        """Sum of actually-received money only - PENDING/PROCESSING attempts and
        CANCELLED ones must never count towards this, or revenue gets overstated."""
        result = await self.db.execute(
            select(func.coalesce(func.sum(TenantPayments.amount), 0)).where(
                TenantPayments.tenant_id == tenant_id,
                TenantPayments.status == TenantPaymentStatus.COMPLETED,
            )
        )
        return result.scalar_one()
