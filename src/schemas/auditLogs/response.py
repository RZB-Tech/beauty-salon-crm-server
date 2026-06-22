from datetime import datetime

from pydantic import BaseModel

class AuditLogsResponseSchema(BaseModel):
    id: int
    table_name: str
    record_id: int
    action: str
    field_name: str
    old_value: str | None = None
    new_value: str | None = None
    changed_by: int
    changed_at: datetime
