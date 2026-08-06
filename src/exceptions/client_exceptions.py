# exceptions/employees.py
from .base import BaseAppException

class ClientNotFound(BaseAppException):
    statusCode = 404
    errorCode = "CLIENT_NOT_FOUND"
    def __init__(self, id: int):
        super().__init__(
            detail=f"Client ID {id} not found",
            errorCode = self.errorCode,
            id = id
        )

class ClientIsInactive(BaseAppException):
    statusCode = 400
    errorCode = "CLIENT_IS_INACTIVE"
    def __init__(self, id: int, firstname: str):
        super().__init__(
            detail=f"Client {firstname} (ID {id}) is inactive",
            errorCode = self.errorCode,
            firstname = firstname,
            id = id
            )

class ClientIsArchived(BaseAppException):
    statusCode = 400
    errorCode = "CLIENT_IS_ARCHIVED"
    def __init__(self, id: int, firstname: str):
        super().__init__(
            detail=f"Client {firstname} (ID {id}) is archived",
            errorCode = self.errorCode,
            firstname = firstname,
            id = id
        )

class DepositOperationHasToBeIn(BaseAppException):
    statusCode = 400
    errorCode = "DEPOSIT_VALUE_HAS_TO_BE_POSITIVE_OR_NEGATIVE_1"
    def __init__(self):
        super().__init__(
            detail=f"Operation has to be 1 (increanse) or -1 (decrease)",
            errorCode = self.errorCode
        )

class DepositCannotBeNegative(BaseAppException):
    statusCode = 400
    errorCode = "DEPOSIT_CANNOT_BE_NEGATIVE"
    def __init__(self):
        super().__init__(
            detail=f"Deposit cannot be negative",
            errorCode = self.errorCode
        )

class DepositNotEnough(BaseAppException):
    statusCode = 409
    errorCode = "CLIENT_DOES_NOT_HAVE_ENOUGH_DEPOSIT"
    def __init__(self, id: int, firstname: str, required: int, has: int):
        super().__init__(
            detail = f"Client's ({firstname}, ID {id}) deposit does not have enough amount ({required})",
            errorCode = self.errorCode,
            id = id,
            firstname = firstname,
            required = required,
            has = has
        )