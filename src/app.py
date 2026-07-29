from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.admin.setup import init_admin
from src.core.exceptions import register_exception_handlers
from src.database.audit_listener import register_audit_listener
from src.routes import protected_router, open_router

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

init_admin(app)

@app.get("/health",
         status_code = 200,
         summary = "Проверка работоспособности",
         description = "Технический эндпоинт для проверки, что сервис запущен и отвечает на запросы.",
         dependencies = [])
async def root_path(): return "healthy"