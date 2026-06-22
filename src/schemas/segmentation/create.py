from typing import Any
from pydantic import BaseModel

class SegmentationCreateSchema(BaseModel):
    name: str
    description: str | None = None
    criteria: dict[str | Any]
    clients: list[int]