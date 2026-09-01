from datetime import date
from enum import StrEnum
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

class PeriodEnum(StrEnum):
    BY_DAY = "by day"
    BY_WEEK = "by week"
    BY_MONTH = "by month"
    BY_YEAR = "by year"

class TranscationsByPeriod(GetReportWithFilters):
    period: PeriodEnum

    @model_validator(mode = "after")
    def validate_period_type(self) -> Self:

        if self.period == PeriodEnum.BY_YEAR and (
            self.start_date.year == self.end_date.year
        ): raise ValueError("Years has to be different in period by year")

        if self.period == PeriodEnum.BY_MONTH and (
            (self.start_date.month == self.end_date.month)
            and ((self.start_date.year == self.end_date.year))
        ): raise ValueError("Months has to be different in period by month")

        if self.period == PeriodEnum.BY_WEEK and (
            (self.start_date.isocalendar().week == self.end_date.isocalendar().week)
            and (self.start_date.year == self.end_date.year)
            and (self.start_date.month == self.end_date.month)
        ): raise ValueError("Weeks has to be different in period by week")

        if self.period == PeriodEnum.BY_DAY and (self.start_date == self.end_date): 
            raise ValueError("Days has to be different in period by day")
        return self