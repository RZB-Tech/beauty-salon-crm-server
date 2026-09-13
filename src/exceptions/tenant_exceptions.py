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

class BranchDoesNotBelongToTenant(BaseAppException):
    statusCode = 409
    errorCode = "BRANCH_DOES_NOT_BELONG_TO_TENANT"
    def __init__(self, parentID: int, branchID: int):
        super().__init__(
            detail = f"Branch ID {branchID} does not belong to the organization ID {parentID}"
        )