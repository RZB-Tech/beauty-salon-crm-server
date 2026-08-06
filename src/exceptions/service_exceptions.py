from .base import BaseAppException

class ServiceNotFound(BaseAppException):
    statusCode = 404
    errorCode = "SERVICE_NOT_FOUND"
    def __init__(self, id: int):
        super().__init__(
            detail=f"Service ID {id} not found",
            errorCode = self.errorCode,
            id = id
        )

class ServiceOneOrMoreNotFound(BaseAppException):
    statusCode = 404
    errorCode = "SERVICE_ONE_OR_MORE_NOT_FOUND"
    def __init__(self):
        super().__init__(detail=f"One or more Service not found",
                         errorCode = self.errorCode)

class ServiceIsArchived(BaseAppException):
    statusCode = 400
    errorCode = "SERVICE_IS_ARCHIVED"
    def __init__(self, id: int, name: str):
        super().__init__(f"Service {name} (ID {id}) is archived",
                         errorCode = self.errorCode,
                         id = id,
                         name = name)