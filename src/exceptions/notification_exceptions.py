# exceptions/employees.py
from .base import BaseAppException

class NotificationNotFound(BaseAppException):
    statusCode = 404
    errorCode = "NOTIFICATION_NOT_FOUND"
    def __init__(self, id: int):
        super().__init__(
            detail=f"Notification ID {id} not found",
            errorCode = self.errorCode,
            id = id
        )

class NotificationAlreadyRead(BaseAppException):
    statusCode = 409
    errorCode = "NOTIFICATION_ALREADY_READ"
    def __init__(self, id: int):
        super().__init__(
            detail=f"Notification ID {id} has already read",
            errorCode = self.errorCode,
            id = id
        )

class NotificationAlreadyCancelled(BaseAppException):
    statusCode = 409
    errorCode = "NOTIFICATION_ALREADY_CANCELLED"
    def __init__(self, id: int):
        super().__init__(
            detail=f"Notification ID {id} has already cancelled",
            errorCode = self.errorCode,
            id = id
        )