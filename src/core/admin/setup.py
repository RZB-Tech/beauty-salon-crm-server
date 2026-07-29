from fastapi import FastAPI
from sqladmin import Admin

from src.core.admin.auth_backend import AdminAuthBackend
from src.core.admin.views import TenantAdmin, TenantCreateView
from src.core.config import settings
from src.database.session import engine

def init_admin(app: FastAPI) -> Admin:
    admin = Admin(
        app,
        engine,
        base_url = "/admin",
        title = "Salon Platform Admin",
        templates_dir = "src/core/admin/templates",
        authentication_backend = AdminAuthBackend(secret_key = settings.SQLADMIN_SESSION_SECRET),
    )

    admin.add_view(TenantAdmin)
    admin.add_view(TenantCreateView)

    return admin
