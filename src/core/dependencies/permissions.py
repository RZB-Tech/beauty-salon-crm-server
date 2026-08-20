from typing import Literal
from fastapi import Depends
from src.core.cache.permission_cache import get_staff_permissions, set_staff_permissions
from src.core.config import settings
from src.core.dependencies.auth import get_current_staff
from src.core.dependencies.uow import UnitOfWork, get_request_uow
from src.core.permissions import PERMISSION_DOMAIN_MANAGE, PERMISSIONS, PermissionCode, compute_effective_permissions
from src.exceptions.auth_exceptions import AdminPreviligesRequired, NotEnoughPermissions
from src.exceptions.staff_exceptions import StaffNotFound
from src.exceptions.tenant_exceptions import TenantNotFound, TenantOnlyForParent
from src.repository.staff.staff_model import StaffType

async def _resolve_staff_type_and_permissions(staff_id: int, uow: UnitOfWork) -> tuple[str, set[int]]:
    cached = await get_staff_permissions(staff_id)
    if cached is not None:
        return cached["staff_type"], set(cached["permissions"])

    staff = await uow.staffs.get(id = staff_id)
    if staff is None:
        raise StaffNotFound()

    permissions = compute_effective_permissions(staff)
    await set_staff_permissions(staff.id, staff.staff_type, permissions, ttl = settings.REFRESH_TOKEN_EXPIRE_SECONDS)
    return staff.staff_type, set(permissions)

def require_permission(codes: list[int], condition: Literal["all", "or"] = "all"):
    if condition not in ("all", "or"):
        raise ValueError(f"Unsupported condition '{condition}', expected either 'all' or 'or'")

    async def dependency(
        current_staff: dict = Depends(get_current_staff),
        uow: UnitOfWork = Depends(get_request_uow)
    ) -> None:
        staff_type, permissions = await _resolve_staff_type_and_permissions(current_staff["id"], uow)

        if staff_type == StaffType.ADMIN:
            return

        def has_permission(code: int) -> bool:
            if code in permissions:
                return True
            manage_code = PERMISSION_DOMAIN_MANAGE.get(PermissionCode(code))
            return manage_code is not None and manage_code in permissions

        if condition == "all":
            missing = [code for code in codes if not has_permission(code)]
            if missing:
                missing_names = [PERMISSIONS[PermissionCode(code)]["name"] for code in missing]
                formatted = ', '.join(missing_names)
                raise NotEnoughPermissions(formatted)
        else:
            if not any(has_permission(code) for code in codes):
                code_names = [PERMISSIONS[PermissionCode(code)]["name"] for code in codes]
                formatted = ', '.join(code_names)
                raise NotEnoughPermissions(formatted)
    return dependency

async def require_admin(
    current_staff: dict = Depends(get_current_staff),
    uow: UnitOfWork = Depends(get_request_uow)
) -> None:
    staff_type, _ = await _resolve_staff_type_and_permissions(current_staff["id"], uow)
    if staff_type != StaffType.ADMIN:
        raise AdminPreviligesRequired()

async def require_parent_tenant(
    current_staff: dict = Depends(get_current_staff),
    uow: UnitOfWork = Depends(get_request_uow)
) -> None:
    """
    Gates parent-only actions (branch management) independent of staff_type -
    require_permission's ADMIN bypass would otherwise let any branch's own
    admin through, since it only checks permissions, not tenant hierarchy.
    """
    tenant = await uow.tenants.get(id = current_staff["tenant_id"])
    if tenant is None:
        raise TenantNotFound(current_staff["tenant_id"])
    if tenant.parent_id is not None:
        raise TenantOnlyForParent()
