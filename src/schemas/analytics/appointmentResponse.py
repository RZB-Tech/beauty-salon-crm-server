from pydantic import BaseModel

class ApppointmentAnalyticsResponse(BaseModel):
    amount: int
    finished: int
    cancelled: int
    absent: int