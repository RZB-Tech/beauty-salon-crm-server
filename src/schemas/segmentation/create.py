from typing import Any
from pydantic import BaseModel, ConfigDict

class SegmentationCreateSchema(BaseModel):
    name: str
    description: str | None = None
    criteria: dict[str, Any]
    client_ids: list[int]

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "name": "Клиенты с высоким депозитом",
            "description": "Клиенты, у которых депозит превышает 500 000",
            "criteria": {"deposit": {"gte": 500000}},
            "client_ids": [1, 2, 3]
        }
    })
