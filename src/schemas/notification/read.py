from pydantic import BaseModel, Field

class NotificationReadSchema(BaseModel):
    id: int = Field(ge = 1)
    notes: str = Field(min_length = 1)