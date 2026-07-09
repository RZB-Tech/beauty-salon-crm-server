from pydantic import Field
from src.repository.payroll.payroll_model import PayrollType
from src.schemas.base import BaseUpdateSchema

class PayrollUpdateSchema(BaseUpdateSchema):
    id: int = Field(ge = 1)
    amount: int | None = Field(None, ge = 1)
    type: PayrollType | None = None
    notes: str | None = None
    archived: bool | None = None