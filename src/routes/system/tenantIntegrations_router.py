from fastapi import APIRouter, Depends, status

from src.core.dependencies.permissions import require_permission
from src.core.dependencies.uow import make_service_dependency
from src.core.permissions import PermissionCode
from src.schemas.tenant.base import TenantPreferencesSchema
from src.schemas.tenant.update import TenantPreferencesUpdateSchema
from src.services.system.tenantIntegrations_service import TenantIntegrationsService

router = APIRouter()

get_tenant_integrations_service = make_service_dependency(TenantIntegrationsService)

@router.get(
    "",
    response_model=TenantPreferencesSchema,
    status_code=status.HTTP_200_OK,
    summary="Get tenant preferences",
    dependencies=[Depends(require_permission([PermissionCode.TENANT_INTEGRATIONS_READ]))]
)
async def get(
    tenantIntegrationsService: TenantIntegrationsService = Depends(get_tenant_integrations_service),
):
    return await tenantIntegrationsService.get()


# @router.patch(
#     "",
#     response_model=TenantPreferencesSchema,
#     status_code=status.HTTP_200_OK,
#     summary="Update tenant preferences",
# )
# async def update(
#     data: TenantPreferencesUpdateSchema,
#     tenantPreferencesService: TenantPreferencesService = Depends(get_tenant_preferences_service),
# ):
#     return await tenantPreferencesService.update(data)
