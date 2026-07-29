from pydantic import BaseModel, ConfigDict, Field

from src.repository.payroll.payroll_model import PayrollType

class PayrollCreateSchema(BaseModel):
    employee_id: int = Field(ge = 1)
    amount: int = Field(ge = 1)
    type: PayrollType
    notes: str | None = None
    appointment_id: int | None = None

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "employee_id": 1,
            "amount": 200000,
            "type": "bonus",
            "notes": "Премия за перевыполнение плана"
        }
    })