from datetime import date

from pydantic import BaseModel, ConfigDict, Field

class ClientFinanceReportRequest(BaseModel):
    clientID: int = Field(ge = 1)
    start_date: date | None = None
    end_date: date | None = None

    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "clientID": 1,
            "start_date": "2026-01-01",
            "end_date": "2026-12-31"
        }
    })