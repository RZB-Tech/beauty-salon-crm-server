import math
from fastapi import HTTPException, status

from src.core.cache.permission_cache import delete_staff_permissions
from src.core.dependencies.uow import UnitOfWork
from src.repository.staff.roles_model import Role
from src.schemas.base import RequestAllObject
from src.schemas.role.create import RoleCreateSchema
from src.schemas.role.update import RoleUpdateSchema

class RoleService():
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create(self, data: RoleCreateSchema) -> Role:
        role = Role(**data.model_dump())
        return await self.uow.roles.create(role)

    async def update(self, data: RoleUpdateSchema) -> Role:
        dataDict = data.model_dump(exclude = {"id"}, exclude_unset = True)
        result = await self.uow.roles.update(data.id, **dataDict)
        if result is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Роль с ID {data.id} не найдена")

        if "permissions" in dataDict:
            await self._invalidate_staff_cache(data.id)

        return result

    async def get(self, id: int) -> Role:
        result = await self.uow.roles.get(id)
        if result is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Роль с ID {id} не найдена")
        return result

    async def get_all(self, data: RequestAllObject) -> dict:
        items, total_items = await self.uow.roles.get_all(data)

        total_pages = math.ceil(total_items / data.pageSize) if data.pageSize > 0 else 0

        return {
            "items": items,
            "page": data.page,
            "pageSize": data.pageSize,
            "totalItems": total_items,
            "totalPages": total_pages
        }

    async def delete(self, id: int) -> bool:
        await self._invalidate_staff_cache(id)
        return await self.uow.roles.delete(id)

    async def _invalidate_staff_cache(self, role_id: int) -> None:
        staff_ids = await self.uow.roles.get_staff_ids(role_id)
        for staff_id in staff_ids:
            await delete_staff_permissions(staff_id)