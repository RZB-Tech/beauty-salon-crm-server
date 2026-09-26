from decimal import Decimal

from .base import BaseAppException

class TenantNotFound(BaseAppException):
    statusCode = 404
    errorCode = "TENANT_NOT_FOUND"
    def __init__(self, id: int):
        super().__init__(
            detail=f"Tenant {id} not found",
            errorCode = self.errorCode,
            id = id
        )

class TenantIsInactive(BaseAppException):
    statusCode = 409
    errorCode = "TENANT_IS_INACTIVE"
    def __init__(self):
        super().__init__(
            detail = "Tenant is inactive",
            errorCode = self.errorCode
        )

class TenantIntegrationsNotFound(BaseAppException):
    statusCode = 404
    errorCode = "TENANT_INTEGRATIONS_NOT_FOUND"
    def __init__(self):
        super().__init__(
            detail = f"Tenant integrations ID {id} not found",
            errorCode = self.errorCode
        )

class TenantOnlyForParent(BaseAppException):
    statusCode = 403
    errorCode = "ONLY_FOR_PARENT_TENANT"
    def __init__(self):
        super().__init__(
            detail = "This action is only available to the parent organization",
            errorCode = self.errorCode
        )

class TenantInsufficientBalance(BaseAppException):
    statusCode = 409
    errorCode = "TENANT_INSUFFICIENT_BALANCE"
    def __init__(self, tenant_id: int, required: Decimal, has: Decimal):
        super().__init__(
            detail = f"Tenant ID {tenant_id} has insufficient balance, required: {required} has: {has}",
            errorCode = self.errorCode,
            tenant_id = tenant_id,
            required = required,
            has = has
        )

class TenantSubscriptionAlreadyActive(BaseAppException):
    statusCode = 409
    errorCode = "TENANT_SUBSCRIPTION_ALREADY_ACTIVE"
    def __init__(self, tenant_id: int, plan_id: int):
        super().__init__(
            detail = f"Tenant ID {tenant_id} already has an active subscription to plan ID {plan_id}",
            errorCode = self.errorCode,
            tenant_id = tenant_id,
            plan_id = plan_id
        )

class TenantLimitExceeded(BaseAppException):
    statusCode = 409
    errorCode = "TENANT_LIMIT_EXCEEDED"
    def __init__(self, limit_key: str, limit: int, used: int):
        super().__init__(
            detail = f"Subscription limit {limit_key} reached: {used} of {limit} used",
            errorCode = self.errorCode,
            limit_key = limit_key,
            limit = limit,
            used = used
        )

class TenantPaymentNotFound(BaseAppException):
    statusCode = 404
    errorCode = "TENANT_PAYMENT_NOT_FOUND"
    def __init__(self, id: int):
        super().__init__(
            detail = f"Payment ID {id} not found",
            errorCode = self.errorCode,
            id = id
        )

class BranchDoesNotBelongToTenant(BaseAppException):
    statusCode = 409
    errorCode = "BRANCH_DOES_NOT_BELONG_TO_TENANT"
    def __init__(self, parentID: int, branchID: int):
        super().__init__(
            detail = f"Branch ID {branchID} does not belong to the organization ID {parentID}"
        )

class ClickCheckoutAmountInUse(BaseAppException):
    statusCode = 409
    errorCode = "CLICK_CHECKOUT_AMOUNT_IN_USE"
    def __init__(self, amount: Decimal):
        super().__init__(
            detail = f"Another organization is paying {amount} via Click right now - choose a slightly different amount",
            errorCode = self.errorCode,
            amount = amount
        )


class TenantBranchesNotAllowed(BaseAppException):
    statusCode = 403
    errorCode = "SUBSCRIPTION_BRANCHES_NOT_ALLOWED"
    def __init__(self, tenant_id: int):
        super().__init__(
            detail = "The organization's subscription plan doesn't allow creating branches",
            errorCode = self.errorCode,
            tenant_id = tenant_id
        )
