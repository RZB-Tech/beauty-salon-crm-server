from pydantic import Field

from src.repository.payroll.payroll_model import PayrollEnum
from src.schemas.base import BaseUpdateSchema

class PayrollUpdateSchema(BaseUpdateSchema):
    id: int
    employee_id: int | None = Field(None, ge = 1)
    amount: int | None = Field(None, ge = 1)
    type: PayrollEnum | None = None
    notes: str | None = None
    appointment_id: int | None = None