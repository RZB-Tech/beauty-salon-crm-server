from pydantic import BaseModel

class StaffRequestSchema(BaseModel):
    id: int | None = None
    login: str | None = None