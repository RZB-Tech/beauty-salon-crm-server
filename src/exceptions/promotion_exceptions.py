from .base import BaseAppException

class PromotionNotFound(BaseAppException):
    statusCode = 404
    errorCode = "PROMOTION_NOT_FOUND"
    def __init__(self, id: int):
        super().__init__(
            detail=f"Promotion ID {id} not found",
            errorCode = self.errorCode,
            id = id
        )

class PromotionInactive(BaseAppException):
    statusCode = 409
    errorCode = "PROMOTION_IS_INACTIVE"
    def __init__(self, id: int, name: str):
        super().__init__(
            detail = f"Promotion {name} (ID {id}) is inactive",
            errorCode = self.errorCode,
            id = id,
            name = name
        )


class PromotionPromoTypeConditionConflict(BaseAppException):
    statusCode = 409
    errorCode = "PROMOTION_TYPE_CONDITION_CONFLICT"
    def __init__(self, id: int, type: str, conditions: dict):
        super().__init__(
            detail = f"Promotion (ID {id}) with type {type} cannot have conditions {conditions}",
            errorCode = self.errorCode,
            id = id,
            promo_type = type,
            conditions = conditions
        )