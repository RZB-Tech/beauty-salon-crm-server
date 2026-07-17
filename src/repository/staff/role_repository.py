from sqlalchemy import func, select
from src.core.utils.model_filter import apply_dynamic_filters
from src.database.base import BaseRepository
from src.repository.staff.roles_model import Role
from src.repository.staff.staff_roles_model import StaffRole
from src.schemas.base import RequestAllObject

class RoleRepository(BaseRepository[Role]):
    async def create(self, role: Role) -> Role:
        self.db.add(role)
        await self.db.flush()
        await self.db.refresh(role)
        return role

    async def get_by_ids(self, ids: list[int]) -> list[Role]:
        result = await self.db.execute(
            select(Role).where(Role.id.in_(ids))
        )
        return result.scalars().all()

    async def get_staff_ids(self, role_id: int) -> list[int]:
        result = await self.db.execute(
            select(StaffRole.staff_id).where(StaffRole.role_id == role_id)
        )
        return list(result.scalars().all())

    async def get_all(self, data: RequestAllObject) -> tuple[list[Role], int]:
        count_stmt = select(func.count()).select_from(Role)
        stmt = select(Role)
        count_stmt = apply_dynamic_filters(count_stmt, Role, data.filters)
        stmt = apply_dynamic_filters(stmt, Role, data.filters)
        total_items = await self.db.scalar(count_stmt) or 0
        offset_value = (data.page - 1) * data.pageSize
        stmt = stmt.order_by(Role.id.asc()).offset(offset_value).limit(data.pageSize)
        result = await self.db.execute(stmt)
        items = result.scalars().all()
        return items, total_items