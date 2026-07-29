from fastapi import APIRouter, Depends, status

from src.core.dependencies.permissions import require_permission
from src.core.dependencies.uow import make_service_dependency
from src.core.permissions import PermissionCode
from src.schemas.tenant.base import TenantPreferencesSchema
from src.schemas.tenant.update import TenantPreferencesUpdateSchema
from src.services.system.tenantPreferences_service import TenantPreferencesService


router = APIRouter()

get_tenant_preferences_service = make_service_dependency(TenantPreferencesService)


@router.get(
    "",
    response_model=TenantPreferencesSchema,
    status_code=status.HTTP_200_OK,
    summary="Получить настройки организации",
    description="Возвращает настройки текущей организации: тема оформления, часовой пояс, валюта, разрешена ли запись через Telegram-бота, срок отмены оплаты по чеку в часах.",
    dependencies=[Depends(require_permission([PermissionCode.TENANT_PREFERENCES_READ]))]
)
async def get(
    tenantPreferencesService: TenantPreferencesService = Depends(get_tenant_preferences_service),
):
    return await tenantPreferencesService.get()


@router.patch(
    "",
    response_model=TenantPreferencesSchema,
    status_code=status.HTTP_200_OK,
    summary="Обновить настройки организации",
    description="Обновляет настройки организации. Передаются только изменяемые поля, остальные сохраняют текущее значение.",
    dependencies=[Depends(require_permission([PermissionCode.TENANT_PREFERENCES_UPDATE]))]
)
async def update(
    data: TenantPreferencesUpdateSchema,
    tenantPreferencesService: TenantPreferencesService = Depends(get_tenant_preferences_service),
):
    return await tenantPreferencesService.update(data)
