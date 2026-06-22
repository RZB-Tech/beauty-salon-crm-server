from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from src.core.utils.model_filter import apply_dynamic_filters
from src.database.base import BaseRepository
from src.repository.employee.employee_model import Employee
from src.repository.employee.workSchedule_model import WorkSchedule
from src.repository.service.service_model import Service
from src.schemas.base import RequestAllObject
from src.schemas.employee.update import EmployeeUpdateSchema

class EmployeeRepository(BaseRepository):
    async def create(self, employee: Employee) -> Employee:
        self.db.add(employee)
        await self.db.commit()
        stmt = (
            select(Employee)
            .where(Employee.id == employee.id)
            .options(selectinload(Employee.services))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

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
        stmt = stmt.options(selectinload(Employee.services)).offset(offset_value).limit(data.pageSize)
        result = await self.db.execute(stmt)
        items = list(result.scalars().all())
        return items, total_items

    async def get_by_ids(self, ids: list[int]) -> list[Employee]:
        result = await self.db.execute(
            select(Employee)
            .where(Employee.id.in_(ids))
            .options(selectinload(Employee.services))
        )
        return list(result.scalars().all())
    
    async def update(self, data: EmployeeUpdateSchema, services: list[Service] | None = None) -> Employee | None:
        obj = await self.db.get(Employee, data.id)
        if not obj:
            return None

        update_data = data.model_dump(exclude_unset=True)
        update_data.pop("id", None)
        update_data.pop("services", None)

        for field, value in update_data.items():
            setattr(obj, field, value)

        if services is not None:
            obj.services = services 

        await self.db.commit()
        await self.db.refresh(obj)

        return obj
    
    async def delete(self, id: int) -> bool:
        obj = await self.db.get(Employee, id)
        if not obj:
            return False

        await self.db.delete(obj)
        await self.db.commit()
        return True