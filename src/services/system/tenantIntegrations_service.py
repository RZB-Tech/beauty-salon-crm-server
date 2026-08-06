from src.core.dependencies.uow import UnitOfWork
from src.exceptions.tenant_exceptions import TenantIntegrationsNotFound
from src.repository.tenant.tenant_model import TenantIntegration

class TenantIntegrationsService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get(self) -> TenantIntegration:
        result = await self.uow.tenantIntegrations.get(self._current_tenant_id())
        if result is None: raise TenantIntegrationsNotFound()
        return result