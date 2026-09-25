from .base import BaseAppException

class SubscriptionPlanNotFound(BaseAppException):
    statusCode = 404
    errorCode = "SUBSCRIPTION_PLAN_NOT_FOUND"
    def __init__(self, id: int):
        super().__init__(
            detail=f"Subscription plan with {id} not found",
            errorCode = self.errorCode,
            id = id
        )

class AddonProductNotFound(BaseAppException):
    statusCode = 404
    errorCode = "ADDON_PRODUCT_NOT_FOUND"
    def __init__(self, id: int):
        super().__init__(
            detail=f"Addon product with {id} not found",
            errorCode = self.errorCode,
            id = id
        )
