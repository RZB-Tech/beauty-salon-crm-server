# exceptions/base.py
class BaseAppException(Exception):
    """Base application exception."""
    status_code: int = 400
    detail: str = "An unexpected error occurred"

    def __init__(self, detail: str = None):
        if detail:
            self.detail = detail
        super().__init__(self.detail)