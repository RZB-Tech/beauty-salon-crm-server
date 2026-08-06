from .base import BaseAppException

class PayrollNotFound(BaseAppException):
    statusCode = 404
    errorCode = "PAYROLL_NOT_FOUND"
    def __init__(self, id: int):
        super().__init__(
            detail=f"Payroll ID {id} not found",
            errorCode = self.errorCode,
            id = id
        )

class PayrollIsArchived(BaseAppException):
    statusCode = 409
    errorCode = "PAYROLL_IS_ARCHIVED"
    def __init__(self, id: int):
        super().__init__(
            detail=f"Payroll (ID {id}) is archived",
            errorCode = self.errorCode,
            id = id
        )

class PayrollIsPaid(BaseAppException):
    statusCode = 409
    errorCode = "PAYROLL_IS_PAID"
    def __init__(self, id: int):
        super().__init__(
            detail = f"Payroll ID {id} is paid",
            errroCode = self.errorCode,
            id = id
        )

class PayrollHasPayout(BaseAppException):
    statusCode = 409
    errorCode = "PAYROLL_HAS_PAYOUT"
    def __init__(self, id: int):
        super().__init__(
            detail = f"Payroll {id} can be changed if has its Payout",
            errorCode = self.errorCode
        )

class PayrollIsCancelled(BaseAppException):
    statusCode = 409
    errorCode = "PAYROLL_IS_CANCELLED"
    def __init__(self, id: int):
        super().__init__(
            detail = f"Payroll {id} is cancelled",
            errorCode = self.errorCode
        )

class PayrollOneOrMoreNotFound(BaseAppException):
    statusCode = 409
    errorCode = "PAYROLL_ONE_OR_MORE_NOT_FOUND"
    def __init__(self):
        super().__init__(
            detail = f"One or more payrolls not found",
            errorCode = self.errorCode
        )

class PayrollNotAttachedToEmployee(BaseAppException):
    statusCode = 409
    errorCode = "PAYROLL_IS_NOT_ATTACHED_TO_EMPLOYEE"
    def __init__(self, payroll_id: int, employee_id: int):
        super().__init__(
            detail = f"Payroll ID {payroll_id} is not attached to Employee {employee_id}",
            errorCode = self.errorCode,
            payroll_id = payroll_id,
            employee_id = employee_id
        )