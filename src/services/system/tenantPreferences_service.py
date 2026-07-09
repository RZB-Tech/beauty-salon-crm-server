from fastapi import HTTPException, status
from src.core.dependencies.context import get_current_tenant_id
from src.core.dependencies.uow import UnitOfWork
from src.repository.tenant.tenant_model import TenantPreferences
from src.schemas.tenant.base import TenantPreferencesSchema
from src.schemas.tenant.update import TenantPreferencesUpdateSchema

class TenantPreferencesService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get(self) -> TenantPreferencesSchema:
        preferences = await self._get_or_create()
        return TenantPreferencesSchema(**preferences.preferences)

    async def update(self, data: TenantPreferencesUpdateSchema) -> TenantPreferencesSchema:
        tenant_id = self._current_tenant_id()
        current = await self._get_or_create()
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        merged_preferences = {
            **TenantPreferencesSchema(**current.preferences).model_dump(),
            **update_data,
        }

        updated = await self.uow.tenantPreferences.update_by_tenant_id(
            tenant_id,
            merged_preferences,
        )
        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Настройки организации не найдены",
            )
        return TenantPreferencesSchema(**updated.preferences)

    async def _get_or_create(self) -> TenantPreferences:
        tenant_id = self._current_tenant_id()
        preferences = await self.uow.tenantPreferences.get_by_tenant_id(tenant_id)
        if preferences is not None:
            return preferences

        default_preferences = TenantPreferencesSchema().model_dump()
        return await self.uow.tenantPreferences.create(
            TenantPreferences(
                tenant_id=tenant_id,
                preferences=default_preferences,
            )
        )

    def _current_tenant_id(self) -> int:
        tenant_id = get_current_tenant_id()
        if tenant_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not resolve tenant context",
            )
        return tenant_id
