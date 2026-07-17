import math
import secrets
import string

from fastapi import HTTPException

from src.core.cache.permission_cache import set_staff_permissions
from src.core.config import settings
from src.core.dependencies.uow import UnitOfWork
from src.core.permissions import compute_effective_permissions
from src.repository.employee.employee_model import Employee
from src.repository.staff.staff_model import Staff
from src.schemas.base import RequestAllObject
from src.schemas.staff.create import StaffCreateAPISchema
from src.core.auth.security import hash_password
from src.schemas.staff.request import StaffPermissionsUpdateSchema, StaffRequestSchema, StaffRolesAssignSchema

class StaffService():
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create(self, data: StaffCreateAPISchema) -> Staff:
        checkLogin = await self.uow.staffs.get(login = data.login.lower())
        if checkLogin: raise HTTPException(409, "Такой логин уже занят")

        employee: Employee | None = None
        if data.employee_id:
            employee = await self.uow.employees.get(data.employee_id)
            if employee is None: raise HTTPException(404)

        roles = []
        if data.roles:
            roles = await self.uow.roles.get_by_ids(data.roles)
            if len(roles) != len(data.roles):
                raise HTTPException(404, "Одна или несколько указанных ролей не найдены")

        exclude = {"password", "roles"}
        if employee: exclude |= {"firstname", "lastname", "middlename"}
        if data.permissions is None: exclude.add("permissions")

        plainPassword = data.password if data.password else self._generate_password()

        staffData = data.model_dump(exclude = exclude)
        staffData["hashed_password"] = hash_password(plainPassword)
        staffData["login"] = data.login.lower()

        staff = Staff(**staffData)
        staff.roles = roles

        created = await self.uow.staffs.create(staff)
        result = await self.uow.staffs.get(id = created.id)
        result.password = plainPassword
        return result

    @staticmethod
    def _generate_password(length: int = 12) -> str:
        alphabet = string.ascii_letters + string.digits + "#@_"
        return "".join(secrets.choice(alphabet) for _ in range(length))

    async def get(self, data: StaffRequestSchema) -> Staff:
        result: Staff | None
        if data.login is not None:
            result = await self.uow.staffs.get(login = data.login.lower())
        else:
            result = await self.uow.staffs.get(id = data.id)
        if not result: raise HTTPException(404)
        return result

    async def get_all(self, data: RequestAllObject) -> dict:
        items, total_items = await self.uow.staffs.get_all(data)

        total_pages = math.ceil(total_items / data.pageSize) if data.pageSize > 0 else 0

        return {
            "items": items,
            "page": data.page,
            "pageSize": data.pageSize,
            "totalItems": total_items,
            "totalPages": total_pages
        }

    async def assign_roles(self, data: StaffRolesAssignSchema) -> Staff:
        staff = await self.uow.staffs.get(id = data.id)
        if staff is None: raise HTTPException(404, f"Сотрудник с ID {data.id} не найден")

        roles = []
        if data.role_ids:
            roles = await self.uow.roles.get_by_ids(data.role_ids)
            if len(roles) != len(data.role_ids):
                raise HTTPException(404, "Одна или несколько указанных ролей не найдены")

        staff.roles = roles
        await self.uow.db.flush()

        refreshed = await self.uow.staffs.get(id = staff.id)
        await self._sync_permissions_cache(refreshed)
        return refreshed

    async def update_permissions(self, data: StaffPermissionsUpdateSchema) -> Staff:
        result = await self.uow.staffs.update(data.id, permissions = data.permissions)
        if result is None: raise HTTPException(404, f"Сотрудник с ID {data.id} не найден")

        refreshed = await self.uow.staffs.get(id = result.id)
        await self._sync_permissions_cache(refreshed)
        return refreshed

    async def _sync_permissions_cache(self, staff: Staff) -> None:
        await set_staff_permissions(
            staff.id,
            staff.staff_type,
            compute_effective_permissions(staff),
            ttl = settings.REFRESH_TOKEN_EXPIRE_SECONDS
        )