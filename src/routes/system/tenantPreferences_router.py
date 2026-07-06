from fastapi import APIRouter, Depends, status

from src.core.dependencies.uow import make_service_dependency
from src.schemas.tenant.base import TenantPreferencesSchema
from src.schemas.tenant.update import TenantPreferencesUpdateSchema
from src.services.system.tenantPreferences_service import TenantPreferencesService


router = APIRouter()

get_tenant_preferences_service = make_service_dependency(TenantPreferencesService)


@router.get(
    "",
    response_model=TenantPreferencesSchema,
    status_code=status.HTTP_200_OK,
    summary="Get tenant preferences",
)
async def get(
    tenantPreferencesService: TenantPreferencesService = Depends(get_tenant_preferences_service),
):
    return await tenantPreferencesService.get()


@router.patch(
    "",
    response_model=TenantPreferencesSchema,
    status_code=status.HTTP_200_OK,
    summary="Update tenant preferences",
)
async def update(
    data: TenantPreferencesUpdateSchema,
    tenantPreferencesService: TenantPreferencesService = Depends(get_tenant_preferences_service),
):
    return await tenantPreferencesService.update(data)
