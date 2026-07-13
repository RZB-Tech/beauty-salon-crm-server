from pydantic import BaseModel, ConfigDict, Field
from src.repository.payroll.payroll_model import PayoutType
from src.schemas.base import BaseResponseSchema
from src.schemas.payroll.response import PayrollResponseSchema

class PayoutResponseSchema(BaseResponseSchema):
    model_config = ConfigDict(from_attributes = True)

    employee_id: int
    type: PayoutType
    notes: str | None = None
    payrolls: list[PayrollResponseSchema] = Field(default_factory = list)
    total_amount: int