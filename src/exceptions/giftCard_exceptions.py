from src.exceptions.base import BaseAppException

class GiftCardNotFound(BaseAppException):
    statusCode = 404
    errorCode = "GIFT_CARD_NOT_FOUND"

    def __init__(self, id: int):
        super().__init__(
            detail = f"Gift card ID {id} not found",
            id = id
        )

class GiftCardCharged(BaseAppException):
    statusCode = 409
    errorCode = "GIFT_CARD_HAS_CHARGED"

    def __init__(self, id: int):
        super().__init__(
            detail = f"Gift card ID {id} has been charged",
            id = id 
        )