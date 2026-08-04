from typing import Any
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload, selectinload
from src.core.utils.model_filter import apply_dynamic_filters
from src.database.base import Actor, BaseRepository
from src.repository.employee.employee_model import Employee
from src.schemas.base import RequestAllObject

class EmployeeRepository(BaseRepository[Employee]):
    async def create(self, employee: Employee) -> Employee:
        self.db.add(employee)
        await self.db.flush()
        stmt = (
            select(Employee)
            .where(Employee.id == employee.id)
            .options(selectinload(Employee.services))
        )
        result = await self.db.execute(stmt)
        return result.scalar()

    async def get(self, id: int) -> Employee | None:
        stmt = (
            select(Employee)
            .where(Employee.id == id)
            .options(selectinload(Employee.services))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all(self, data: RequestAllObject) -> tuple[list[Employee], int]:
        count_stmt = select(func.count()).select_from(Employee)
        stmt = select(Employee)
        count_stmt = apply_dynamic_filters(count_stmt, Employee, data.filters)
        stmt = apply_dynamic_filters(stmt, Employee, data.filters)
        total_items = await self.db.scalar(count_stmt) or 0
        offset_value = (data.page - 1) * data.pageSize
        stmt = stmt.options(selectinload(Employee.services)).order_by(Employee.id.desc()).offset(offset_value).limit(data.pageSize)
        result = await self.db.execute(stmt)
        items = result.scalars().all()
        return items, total_items

    async def get_by_ids(self, ids: list[int]) -> list[Employee]:
        result = await self.db.execute(
            select(Employee)
            .where(Employee.id.in_(ids))
            .options(selectinload(Employee.services))
        )
        return result.scalars().all()

    async def get_all_for_export(self) -> list[Employee]:
        stmt = (
            select(Employee)
            .options(
                selectinload(Employee.specialization),
                selectinload(Employee.services),
            )
            .order_by(Employee.id.asc())
        )

        result = await self.db.execute(stmt)
        return result.scalars().unique().all()