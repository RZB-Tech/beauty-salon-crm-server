from src.schemas.base import BaseUpdateSchema

class ServiceUpdateSchema(BaseUpdateSchema):
    id: int
    name: str | None = None
    price: int | None = None
    category_id: int | None = None