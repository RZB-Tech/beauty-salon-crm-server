from .base import BaseAppException

class SpecializationNotFound(BaseAppException):
    status_code = 404
    def __init__(self, id: int):
        super().__init__(detail=f"Специалиация с ID {id} не найдена")

class SpecializationIsArchived(BaseAppException):
    status_code = 404
    def __init__(self, id: int):
        super().__init__(detail=f"Специалиация с ID {id} архивирована")