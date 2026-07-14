from datetime import date

from pydantic import BaseModel, Field

class EmployeeFinanceReportRequest(BaseModel):
    employeeID: int = Field(ge = 1)
    start_date: date | None = None
    end_date: date | None = None