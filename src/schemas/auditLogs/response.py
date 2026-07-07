from datetime import datetime

from pydantic import BaseModel, ConfigDict

class AuditLogsResponseSchema(BaseModel):
    id: int
    table_name: str
    record_id: int
    action: str

    field_name: str | None = None
    old_value: str | None = None
    new_value: str | None = None

    changed_by: int
    actor_type: str
    actor_display_name: str

    changed_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
