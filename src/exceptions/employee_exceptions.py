# exceptions/employees.py
from .base import BaseAppException

class EmployeeNotFound(BaseAppException):
    statusCode = 404
    errorCode = "EMPLOYEE_NOT_FOUND"
    def __init__(self, id: int):
        super().__init__(
            detail=f"Employee with ID {id} not found",
            errorCode = self.errorCode,
            id = id
        )

class EmployeeInactive(BaseAppException):
    statusCode = 400
    errorCode = "EMPLOYEE_IS_INACTIVE"
    def __init__(self, id: int, firstname: str):
        super().__init__(
            detail=f"Employee {firstname} (ID {id}) is inactive",
            errorCode = self.errorCode,
            firstname = firstname,
            id = id
            )

class EmployeeIsArchived(BaseAppException):
    statusCode = 400
    errorCode = "EMPLOYEE_IS_ARCHIVED"
    def __init__(self, id: int, firstname: str):
        super().__init__(
            detail=f"Employee {firstname} (ID {id}) is archived",
            errorCode = self.errorCode,
            firstname = firstname,
            id = id
        )

class EmployeeDoesNotWork(BaseAppException):
    statusCode = 409
    errorCode = "EMPLOYEE_NOT_HAS_WORK_SCHEDULE"
    def __init__(self, id: int, firstname: str):
        super().__init__(
            detail=f"Employee {firstname} (ID {id}) does no work during these hours",
            errorCode = self.errorCode,
            firstname = firstname,
            id = id
        )

class EmployeeDoesNotProvideService(BaseAppException):
    statusCode = 409
    errorCode = "EMPLOYEE_DOES_NOT_PROVIDE_SERVICE"
    def __init__(self, employee_id: int, firstname: str, service_id: int, name: str):
        super().__init__(
            detail=f"Employee {firstname} (ID {employee_id}) does not provide service {name} (ID {service_id})",
            errorCode = self.errorCode,
            employee_id = employee_id,
            firstname = firstname,
            service_id = service_id,
            name = name 
        )

class EmployeeDoesNotHavePayrolls(BaseAppException):
    statusCode = 404
    errorCode = "EMPLOYEE_DOES_NOT_HAVE_PAYROLLS"
    def __init__(self, id: int):
        super().__init__(
            detail = f"Employee (ID {id}) does not have any Payrolls",
            errorCode = self.errorCode,
            id = id
        )