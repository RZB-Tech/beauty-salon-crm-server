from src.core.cache.tenant_cache import delete_tenant_preferences, get_tenant_preferences, set_tenant_preferences
from src.core.dependencies.context import get_current_tenant_id
from src.core.dependencies.uow import UnitOfWork
from src.exceptions.general_exceptions import CannotUpdate
from src.exceptions.tenant_exceptions import TenantNotFound
from src.schemas.tenant.base import TenantPreferencesSchema
from src.schemas.tenant.update import TenantPreferencesUpdateSchema

class TenantPreferencesService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get(self) -> TenantPreferencesSchema:
        tenant = await self.get_tenant_or_raise(self)
        return TenantPreferencesSchema(**tenant.preferences)

    async def update(self, data: TenantPreferencesUpdateSchema) -> TenantPreferencesSchema:
        tenant = await self.get_tenant_or_raise(self)
        current_prefs = TenantPreferencesSchema(**tenant.preferences).model_dump()
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        
        merged_preferences = {
            **current_prefs,
            **update_data,
        }

        updated_tenant = await self.uow.tenants.update(
            id=tenant.id,
            preferences=merged_preferences,
        )
        
        if updated_tenant is None: raise CannotUpdate(tenant.id, "tenants")

        # Commit, then clear the cache: FastAPI's own commit runs only after the
        # response is sent, and clearing first would let a concurrent read re-cache
        # the old preferences for the whole TTL.
        await self.uow.db.commit()
        await delete_tenant_preferences(tenant.id)

        return TenantPreferencesSchema(**updated_tenant.preferences)

    @staticmethod
    async def get_tenant_or_raise(self):
        """Helper to get the current tenant or raise a 404 if they do not exist."""
        tenant_id = get_current_tenant_id()
        tenant = await self.uow.tenants.get(id=tenant_id)
        if tenant is None: raise TenantNotFound(tenant_id)
        return tenant

async def load_tenant_preferences(uow: UnitOfWork, tenant_id: int) -> TenantPreferencesSchema | None:
    """
    Cache-first preferences of any tenant (not only the current one) - None if the
    tenant doesn't exist. Used where preferences are read on every request, e.g.
    the Telegram mini app's booking checks.
    """
    raw = await get_tenant_preferences(tenant_id)
    if raw is None:
        tenant = await uow.tenants.get(id = tenant_id)
        if tenant is None: return None
        raw = tenant.preferences or {}
        await set_tenant_preferences(tenant_id, raw)
    return TenantPreferencesSchema(**raw)
