from pydantic import BaseModel, Field

from src.repository.payroll.payroll_model import PayrollType

class PayrollCreateSchema(BaseModel):
    employee_id: int = Field(ge = 1)
    amount: int = Field(ge = 1)
    type: PayrollType
    notes: str | None = None
    appointment_id: int | None = None