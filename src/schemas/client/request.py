from datetime import date

from pydantic import BaseModel, Field

class FinanceReportRequest(BaseModel):
    clientID: int = Field(ge = 1)
    start_date: date | None = None
    end_date: date | None = None