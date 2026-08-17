from pydantic import BaseModel, Field

class GiftCardCancelSchema(BaseModel):
    id: int = Field(ge = 1)
    cancelled_reason: str