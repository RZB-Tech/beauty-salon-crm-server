from pydantic import Field
from src.repository.payroll.payroll_model import PayrollType
from src.schemas.base import BaseUpdateSchema, MoneyOptional

class PayrollUpdateSchema(BaseUpdateSchema):
    id: int = Field(ge = 1)
    amount: MoneyOptional
    type: PayrollType | None = None
    notes: str | None = None
    archived: bool | None = None