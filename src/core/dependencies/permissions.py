from typing import Literal
from fastapi import Depends, HTTPException, status
from src.core.cache.permission_cache import get_staff_permissions, set_staff_permissions
from src.core.config import settings
from src.core.dependencies.auth import get_current_staff
from src.core.dependencies.uow import UnitOfWork, get_request_uow
from src.core.permissions import PERMISSIONS, PermissionCode, compute_effective_permissions
from src.repository.staff.staff_model import StaffType

async def _resolve_staff_type_and_permissions(staff_id: int, uow: UnitOfWork) -> tuple[str, set[int]]:
    cached = await get_staff_permissions(staff_id)
    if cached is not None:
        return cached["staff_type"], set(cached["permissions"])

    staff = await uow.staffs.get(id = staff_id)
    if staff is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Пользователь не найден")

    permissions = compute_effective_permissions(staff)
    await set_staff_permissions(staff.id, staff.staff_type, permissions, ttl = settings.REFRESH_TOKEN_EXPIRE_SECONDS)
    return staff.staff_type, set(permissions)

def require_permission(codes: list[int], condition: Literal["all", "or"] = "all"):
    if condition not in ("all", "or"):
        raise ValueError(f"Неподдерживаемое условие '{condition}', ожидается 'all' или 'or'")

    async def dependency(
        current_staff: dict = Depends(get_current_staff),
        uow: UnitOfWork = Depends(get_request_uow)
    ) -> None:
        staff_type, permissions = await _resolve_staff_type_and_permissions(current_staff["id"], uow)

        if staff_type == StaffType.ADMIN:
            return

        if condition == "all":
            missing = [code for code in codes if code not in permissions]
            if missing:
                missing_names = [PERMISSIONS[PermissionCode(code)]["name"] for code in missing]
                raise HTTPException(
                    status_code = status.HTTP_403_FORBIDDEN,
                    detail = f"Недостаточно прав для выполнения действия (требуемые разрешения: {', '.join(missing_names)})"
                )
        else:
            if not any(code in permissions for code in codes):
                code_names = [PERMISSIONS[PermissionCode(code)]["name"] for code in codes]
                raise HTTPException(
                    status_code = status.HTTP_403_FORBIDDEN,
                    detail = f"Недостаточно прав для выполнения действия (требуется одно из разрешений: {', '.join(code_names)})"
                )
    return dependency

async def require_admin(
    current_staff: dict = Depends(get_current_staff),
    uow: UnitOfWork = Depends(get_request_uow)
) -> None:
    staff_type, _ = await _resolve_staff_type_and_permissions(current_staff["id"], uow)
    if staff_type != StaffType.ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Доступно только администратору")
