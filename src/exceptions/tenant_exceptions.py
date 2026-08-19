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

class TenantCannotCreateBranch(BaseAppException):
    statusCode = 403
    errorCode = "TENANT_CANNOT_CREATE_BRANCH"
    def __init__(self):
        super().__init__(
            detail = "Only a parent organization can create branches",
            errorCode = self.errorCode
        )