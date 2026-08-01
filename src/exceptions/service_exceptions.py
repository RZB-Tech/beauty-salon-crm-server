from .base import BaseAppException

class ServiceNotFound(BaseAppException):
    status_code = 404
    def __init__(self, id: int):
        super().__init__(detail=f"Услуга с ID {id} не найдена")

class ServiceOneOrMoreNotFound(BaseAppException):
    status_code = 404
    def __init__(self):
        super().__init__(detail=f"Одна или несколько указанных услуг не найдены")

class ServiceIsArchived(BaseAppException):
    status_code = 400
    def __init__(self, id: int, name: str):
        super().__init__(f"Услуга {name} (ID {id}) архивирована")