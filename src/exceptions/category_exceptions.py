from .base import BaseAppException

class ServiceCategoryNotFound(BaseAppException):
    statusCode = 404
    errorCode = "SERVICE_CATEGORY_NOT_FOUND"
    def __init__(self, id: int):
        super().__init__(
            detail=f"Service's category ID {id} not found",
            errorCode = self.errorCode,
            id = id)

class ServiceCategoryIsArchived(BaseAppException):
    statusCode = 409
    errorCode = "SERVICE_CATEGORY_IS_ARCHIVED"
    def __init__(self, id: int, name: str):
        super().__init__(
            detail = f"Service's category {name} (ID {id}) is archived",
            errorCode = self.errorCode,
            id = id,
            name = name)