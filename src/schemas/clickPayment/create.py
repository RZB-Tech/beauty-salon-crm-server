from pydantic import BaseModel
from src.schemas.base import MoneyRequired

class ClickCheckoutCreateSchema(BaseModel):
    amount: MoneyRequired
