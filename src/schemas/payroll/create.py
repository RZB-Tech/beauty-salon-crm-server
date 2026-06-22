from pydantic import BaseModel, Field

from src.repository.payroll.payroll_model import PayrollEnum

class PayrollCreateSchema(BaseModel):
    employee_id: int = Field(ge = 1)
    amount: int = Field(ge = 1)
    type: PayrollEnum
    notes: str | None = None
    appointment_id: int | None = None