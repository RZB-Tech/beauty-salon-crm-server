from typing import Any
from pydantic import ConfigDict
from src.schemas.base import BaseResponseSchema

class SegmentationResponseSchema(BaseResponseSchema):
    name: str
    description: str | None = None
    criteria: dict[str, Any]
    client_ids: list[int]

    model_config = ConfigDict(from_attributes = True)