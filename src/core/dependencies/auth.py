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

    if login is None or id is None: raise credentials_exception

    set_current_staff_id(id)

    return {"id": id, "login": login}

async def get_current_staff_ws(websocket: WebSocket) -> dict | None:
    print("=== WS Auth Debug ===")
    print(f"Cookies: {websocket.cookies}")
    print(f"Headers: {dict(websocket.headers)}")

    token = websocket.cookies.get("access_token")
    print(f"Token: {token}")

    if token is None:
        print("❌ No token in cookies")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None

    payload = decode_token(token)
    print(f"Payload: {payload}")

    if payload is None:
        print("❌ Invalid token")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None

    login: str = payload.get("sub")
    id: int    = payload.get("id")
    print(f"Login: {login}, ID: {id}")

    if login is None or id is None:
        print("❌ Missing sub or id in payload")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None

    set_current_staff_id(id)
    print(f"✅ Auth success: {login}")
    return {"id": id, "login": login}