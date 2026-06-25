from fastapi import HTTPException, Request, WebSocket, status

from src.core.auth.security import decode_token
from src.core.dependencies.context import set_current_staff_id

async def get_current_staff(request: Request) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )
    
    token = request.cookies.get("access_token")
    if token is None:
        raise credentials_exception
    
    payload = decode_token(token)
    if payload is None: raise credentials_exception

    login: str = payload.get("sub")
    id: int = payload.get("id")
    tenant_id: int = payload.get("tenant_id")

    if login is None or id is None: raise credentials_exception

    set_current_staff_id(id, tenant_id)

    return {
        "id": id, 
        "login": login, 
        "tenant_id": tenant_id
        }