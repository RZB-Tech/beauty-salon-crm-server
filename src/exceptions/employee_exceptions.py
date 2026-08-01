# exceptions/employees.py
from .base import BaseAppException

class EmployeeNotFound(BaseAppException):
    status_code = 404
    def __init__(self, employee_id: int):
        super().__init__(detail=f"Сотрудник с ID {employee_id} не найден")

class EmployeeNotActive(BaseAppException):
    status_code = 400
    def __init__(self, employee_id: int, firstname: str):
        super().__init__(detail=f"Сотрудник {firstname} (ID {employee_id}) неактивен")

class EmployeeIsArchived(BaseAppException):
    status_code = 400
    def __init__(self, employee_id: int, firstname: str):
        super().__init__(detail=f"Сотрудник {firstname} (ID {employee_id}) архивирован")