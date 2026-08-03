from fastapi import HTTPException
from src.core.dependencies.context import get_current_tenant_id
from src.core.dependencies.uow import UnitOfWork
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
        
        if updated_tenant is None: raise HTTPException(404, "Организация не найдена")
            
        return TenantPreferencesSchema(**updated_tenant.preferences)

    @staticmethod
    async def get_tenant_or_raise(self):
        """Helper to get the current tenant or raise a 404 if they do not exist."""
        tenant_id = get_current_tenant_id()
        tenant = await self.uow.tenants.get(id=tenant_id)
        if tenant is None: raise HTTPException(404, "Организация не найдена")
        return tenant
