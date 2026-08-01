from .base import BaseAppException

class ServiceCategoryNotFound(BaseAppException):
    status_code = 404
    def __init__(self, id: int):
        super().__init__(detail=f"Категория с ID {id} не найдена")

class ServiceCategoryIsArchived(BaseAppException):
    status_code = 409
    def __init__(self, id: int, name: str):
        super().__init__(f"Категория {name} (ID {id}) архивирована")