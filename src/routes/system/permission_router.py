from fastapi import APIRouter, Depends
from src.core.dependencies.permissions import require_admin
from src.core.permissions import PERMISSIONS
from src.schemas.permission.response import PermissionResponseSchema

router = APIRouter(dependencies = [Depends(require_admin)])

@router.get(
    "",
    response_model = list[PermissionResponseSchema],
    status_code = 200,
    summary = "List available permission codes"
)
async def get_all() -> list[PermissionResponseSchema]:
    return [
        PermissionResponseSchema(code = code, resource = meta["resource"], name = meta["name"])
        for code, meta in PERMISSIONS.items()
    ]