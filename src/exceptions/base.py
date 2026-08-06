class BaseAppException(Exception):
    statusCode: int = 500
    errorCode: str = "INTERNAL_ERROR"
    detail: str = "An unexpected error occurred"

    def __init__(self, detail: str = None, errorCode: str = None, statusCode: int = None, **metadata):
        if detail is not None: self.detail = detail
        if errorCode is not None: self.errorCode = errorCode
        if statusCode is not None: self.statusCode = statusCode
        self.metadata = metadata
        super().__init__(self.detail)