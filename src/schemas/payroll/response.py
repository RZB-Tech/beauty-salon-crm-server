from src.repository.payroll.payroll_model import PayrollType
from src.schemas.base import BaseResponseSchema, MoneyResponse

class PayrollResponseSchema(BaseResponseSchema):
    employee_id: int
    amount: MoneyResponse
    type: PayrollType
    notes: str | None = None
    payout_id: int | None = None
    status: str
    appointment_id: int | None = None