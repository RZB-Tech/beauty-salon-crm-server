from pydantic import BaseModel

class PermissionResponseSchema(BaseModel):
    code: int
    resource: str
    name: str