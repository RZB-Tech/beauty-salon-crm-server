from .base import BaseAppException

class PayoutNotFound(BaseAppException):
    statusCode = 404
    errorCode = "PAYOUT_NOT_FOUND"
    def __init__(self, id: int):
        super().__init__(
            detail=f"Payout ID {id} not found",
            errorCode = self.errorCode,
            id = id
        )

class PayoutIsCancelled(BaseAppException):
    statusCode = 409
    errorCode = "PAYOUT_IS_CANCELLED"
    def __init__(self, id: int):
        super().__init__(
            detail = f"Payout ID {id} is cancelled",
            errorCode = self.errorCode,
            id = id
        )