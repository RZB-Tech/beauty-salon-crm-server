# exceptions/employees.py
from .base import BaseAppException

class RoleNotFound(BaseAppException):
    statusCode = 404
    errorCode = "ROLE_NOT_FOUND"
    def __init__(self, id: int):
        super().__init__(
            detail = f"Role ID {id} not found",
            errorCode = self.errorCode,
            id = id
        )

class RoleOneOrMoreNotFound(BaseAppException):
    statusCode = 404
    errorCode = "ROLE_ONE_OR_MORE_NOT_FOUND"
    def __init__(self):
        super().__init__(
            detail = "One or more roles not found", 
            errorCode = self.errorCode
        )