from src.schemas.base import BaseUpdateSchema

class ServiceUpdateSchema(BaseUpdateSchema):
    id: int
    name: str | None = None
    category_id: int | None = None