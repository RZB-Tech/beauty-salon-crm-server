from datetime import date
from typing import Self

from pydantic import BaseModel, model_validator

class GetReportWithFilters(BaseModel):
    start_date: date
    end_date: date

    @model_validator(mode = "after")
    def validate_period(self) -> Self:
        if self.start_date > self.end_date:
            raise ValueError("End date has to be later than start date!")
        return self