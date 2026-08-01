from .base import BaseAppException

class AbsenceNotFound(BaseAppException):
    status_code = 404
    def __init__(self, id: int):
        super().__init__(detail=f"Отсутствие с ID {id} не найдено")

class AbsenceIsArchived(BaseAppException):
    status_code = 400
    def __init__(self, id: int):
        super().__init__(f"Отсутствие (ID {id}) архивировано")