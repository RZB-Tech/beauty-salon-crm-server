from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from src.core.utils.model_filter import apply_dynamic_filters
from src.database.base import BaseRepository
from src.repository import Material
from src.schemas.base import RequestAllObject
from src.schemas.material.create import MaterialCreateSchema
from src.schemas.material.update import MaterialUpdateSchema

class MaterialRepository(BaseRepository):
    async def create(self, material: Material) -> Material:
        self.db.add(material)
        # await self.db.commit()
        # await self.db.refresh(material)
        await self.db.flush()
        return material
    
    async def get_by_ids(self, ids: list[int]) -> list[Material]:
        result = await self.db.execute(
            select(Material).where(Material.id.in_(ids))
        )
        return list(result.scalars().all())
    
    async def get(self, id: int) -> Material | None:
        return await self.db.get(Material, id)
    
    async def get_all(self, data: RequestAllObject) -> tuple[list[Material], int]:
        count_stmt = select(func.count()).select_from(Material)
        stmt = select(Material)
        count_stmt = apply_dynamic_filters(count_stmt, Material, data.filters)
        stmt = apply_dynamic_filters(stmt, Material, data.filters)
        total_items = await self.db.scalar(count_stmt) or 0
        offset_value = (data.page - 1) * data.pageSize
        stmt = stmt.offset(offset_value).limit(data.pageSize)
        result = await self.db.execute(stmt)
        items = list(result.scalars().all())
        return items, total_items
    
    async def update(self, payload: MaterialUpdateSchema) -> Material | None:
        obj = await self.db.get(Material, payload.id)
        if not obj:
            return None

        update_data = payload.model_dump(exclude_unset=True)
        update_data.pop("id", None)

        for field, value in update_data.items():
            setattr(obj, field, value)

        return obj
    
    async def delete(self, id: int) -> bool:
        obj = await self.db.get(Material, id)
        if not obj:
            return False

        await self.db.delete(obj)
        return True
    
    async def updateQuantity(self, material: Material, quantity: int) -> Material:
        material.quantity = quantity
        return material