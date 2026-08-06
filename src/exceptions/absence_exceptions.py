from .base import BaseAppException

class AbsenceNotFound(BaseAppException):
    statusCode = 404
    errorCode = "ABSENCE_NOT_FOUND"
    def __init__(self, id: int):
        super().__init__(
            detail=f"Absence ID {id} not found",
            errorCode = self.errorCode,
            id = id)

class AbsenceIsArchived(BaseAppException):
    statusCode = 400
    errorCode = "ABSENCE_IS_ARCHIVED"
    def __init__(self, id: int):
        super().__init__(
            detail = f"Absence (ID {id}) is archived",
            errorCode = self.errorCode,
            id = id)