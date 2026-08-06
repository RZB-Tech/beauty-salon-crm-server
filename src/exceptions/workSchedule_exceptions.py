# exceptions/employees.py
from .base import BaseAppException

class WorkScheduleNotFound(BaseAppException):
    statusCode = 404
    errorCode = "WORK_SCHEDULE_NOT_FOUND"
    def __init__(self, id: int):
        super().__init__(
            detail=f"Work schedule {id} not found",
            errorCode = self.errorCode,
            id = id
        )