from src.repository.payroll.payroll_model import PayrollEnum
from src.schemas.base import BaseResponseSchema

class PayrollResponseSchema(BaseResponseSchema):
    employee_id: int
    amount: int
    type: PayrollEnum
    notes: str | None = None
    appointment_id: int | None = None