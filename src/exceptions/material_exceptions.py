from .base import BaseAppException

class MaterialNotFound(BaseAppException):
    statusCode = 404
    errorCode = "MATERIAL_NOT_FOUND"
    def __init__(self, id: int):
        super().__init__(
            detail=f"Material ID {id} not found",
            errorCode = self.errorCode,
            id = id
        )

class MaterialArchived(BaseAppException):
    statusCode = 409
    errorCode = "MATERIAL_IS_ARCHIVED"
    def __init__(self, id: int, name: str):
        super().__init__(
            detail=f"Material {name} (ID {id}) is archived",
            errorCode = self.errorCode,
            id = id
        )

class MaterialAmountInsufficient(BaseAppException):
    statusCode = 409
    errorCode = "MATERIAL_AMOUNT_IS_NOT_SUFFICIENT"
    def __init__(self, id: int, name: str, requested: int, has: int):
        super().__init__(
            detail=f"Material {name} (ID {id}) has not enough amount",
            errorCode = self.errorCode,
            id = id,
            name = name,
            requested = requested,
            has = has
        )