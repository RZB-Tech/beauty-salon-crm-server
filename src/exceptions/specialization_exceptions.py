from .base import BaseAppException

class SpecializationNotFound(BaseAppException):
    statusCode = 404
    errorCode = "SPECIALIZATION_NOT_FOUND"
    def __init__(self, id: int):
        super().__init__(
            detail=f"Specialization ID {id} not found",
            errorCode = self.errorCode,
            id = id)

class SpecializationIsArchived(BaseAppException):
    statusCode = 404
    errorCode = "SPECIALIZATION_IS_ARCHIVED"
    def __init__(self, id: int, name: str):
        super().__init__(
            detail=f"Specialization {name} (ID {id}) is archived",
            errorCode = self.errorCode,
            id = id,
            name = name)