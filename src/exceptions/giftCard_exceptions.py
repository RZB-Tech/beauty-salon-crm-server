from src.exceptions.base import BaseAppException
from src.repository.giftCard.giftCard_model import GiftCardStatus

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

class GiftCardInsufficientAmount(BaseAppException):
    statusCode = 409
    errorCode = "GIFT_CARD_INSUFFICIENT_AMOUNT"

    def __init__(self, id: int, requested: int, has: int):
        super().__init__(
            detail = f"Gift card ID {id} has insufficient amount, requested: {requested} has: {has}",
            id = id,
            requested = requested,
            has = has
        )

class GiftCardCancelled(BaseAppException):
    statusCode = 409
    errorCode = "GIFT_CARD_CANCELLED"

    def __init__(self, id: int):
        super().__init__(
            detail = f"Gift card ID {id} is cancelled",
            id = id
        )        

class GiftCardUnusable(BaseAppException):
    statusCode = 409
    errorCode = "GIFT_CARD_UNSABLE"

    def __init__(self, id: int, status: str):
        super().__init__(
            detial = f"Gift card ID {id} is unusable, reasons: {status}",
            id = id,
            status = status
        )

class GiftCardClientConflict(BaseAppException):
    statusCode = 409
    errorCode = "GIFT_CARD_CLIENT_CONFLICT"

    def __init__(self, giftCard_id: int, client_id: int):
        super().__init__(
            detail = f"Gift card ID {giftCard_id} is not attached to client ID {client_id}",
            giftCard_id = giftCard_id,
            client_id = client_id
        )        