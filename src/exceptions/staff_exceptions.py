# exceptions/employees.py
from .base import BaseAppException

class StaffIsInactive(BaseAppException):
    statusCode = 409
    errorCode = "STAFF_IS_INACTIVE"
    def __init__(self):
        super().__init__(
            detail="Staff is inactive",
            errorCode = self.errorCode
        )

class StaffNotFound(BaseAppException):
    statusCode = 404
    errorCode = "STAFF_NOT_FOUND"
    def __init__(self):
        super().__init__(
            detail="Staff not found",
            errorCode = self.errorCode
        )