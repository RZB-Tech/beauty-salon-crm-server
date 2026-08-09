from .base import BaseAppException

class AuthTenantContextEmpty(BaseAppException):
    statusCode = 404
    errorCode = "AUTH_OR_TENANT_CONTEXT_EMPTY"
    def __init__(self):
        super().__init__(
            detail=f"Auth or tenant context is empty",
            errorCode = self.errorCode
        )

class IncorrectCredentials(BaseAppException):
    statusCode = 401
    errorCode = "INCORRECT_CREDENTIALS"
    def __init__(self):
        super().__init__(
            detail="Incorrect credentials",
            errorCode = self.errorCode
        )

class IncorrectOldPassword(BaseAppException):
    statusCode = 401
    errorCode = "INCORRECT_OLD_PASSWORD"
    def __init__(self):
        super().__init__(
            detail="Incorrect old password",
            errorCode = self.errorCode
        )

class TenantIsInactive(BaseAppException):
    statusCode = 403
    errorCode = "TENANT_IS_INACTIVE"
    def __init__(self):
        super().__init__(
            detail="Organization is inactive",
            errorCode = self.errorCode
        )

class RefreshTokenMissing(BaseAppException):
    statusCode = 401
    errorCode = "REFRESH_TOKEN_MISSING"
    def __init__(self):
        super().__init__(
            detail="Refresh token is missing",
            errorCode = self.errorCode
        )

class TokenIsInvalid(BaseAppException):
    statusCode = 401
    errorCode = "INVALID_TOKEN"
    def __init__(self):
        super().__init__(
            detail="Token is invalid",
            errorCode = self.errorCode
        )

class AdminPreviligesRequired(BaseAppException):
    statusCode = 403
    errorCode = "ADMIN_PREVILIGES_REQUIRED"
    def __init__(self):
        super().__init__(
            detail="Required administrator staff type",
            errorCode = self.errorCode
        )

class NotEnoughPermissions(BaseAppException):
    statusCode = 403
    errorCode = "NOT_ENOUGH_PERMISSIONS"
    def __init__(self, permissions: str):
        super().__init__(
            detail = f"User does not have enough permissions: {permissions}",
            errorCode = self.errorCode,
            required_permissions = permissions
        )

class PermissionNotFound(BaseAppException):
    statusCode = 404
    errorCode = "PERMISSION_NOT_FOUND"
    def __init__(self, code: int):
        super().__init__(
            detail = f"Permission {code} not found",
            errorCode = self.errorCode,
            code = code
        )