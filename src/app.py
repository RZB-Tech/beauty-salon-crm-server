from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from src.core.dependencies.auth import get_current_staff_ws
from src.core.exceptions import register_exception_handlers
from src.database.audit_listener import register_audit_listener
from src.routes import protected_router, open_router
from src.core.utils.ws_connection_manage import manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    register_audit_listener()
    yield

app = FastAPI(lifespan = lifespan,
            title = "Beauty salon",
            swagger_ui_parameters = {
                "defaultModelsExpandDepth": -1
            })

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]    
)

register_exception_handlers(app)

app.include_router(open_router)
app.include_router(protected_router)

@app.get("/health",
         status_code = 200,
         dependencies = [])
async def root_path(): return "healthy"

# @app.router.websocket("/api/v1/notifications/ws")
# async def notification_stream(websocket: WebSocket):
#     await websocket.accept()
#     staff = await get_current_staff_ws(websocket)
#     if staff is None: return 

#     await manager.connect(websocket, staff["id"])
#     try: 
#         while True: await websocket.receive_text()
#     except WebSocketDisconnect:
#         manager.disconnect(websocket, staff["id"])