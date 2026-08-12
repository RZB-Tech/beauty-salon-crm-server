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

class PromotionTargetConflict(BaseAppException):
    statusCode = 409
    errorCode = "PROMOTION_HAS_CONFLICT_WITH_TARGET"
    def __init__(self, target: str, target_id: int, promotion_id: int, promotion_name: str):
        super().__init__(
            detail = f"{target.capitalize()} (ID {target_id}) already has active promotion {promotion_name} (ID {promotion_id})",
            errorCode = self.errorCode,
            target = target,
            target_id = target_id,
            promotion_id = promotion_id
        )

class PromotionDiscountPercentageExceed(BaseAppException):
    statusCode = 400
    errorCode = "PROMOTION_DISCOUNT_PERCENTAGE_EXCEED"
    def __init__(self, value: int):
        super().__init__(
            detail = "Promotion's discount with type 'percentage' has to be between 0 and 100",
            errorCode = self.errorCode,
            value = value
        )