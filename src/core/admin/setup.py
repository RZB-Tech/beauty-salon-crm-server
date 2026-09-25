from fastapi import FastAPI
from sqladmin import Admin

from src.core.admin.auth_backend import AdminAuthBackend
from src.core.admin.views import AddonProductAdmin, SubscriptionPlanAdmin, TenantAddonAdmin, TenantAdmin, TenantCreateView, TenantSubscriptionAdmin
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
    admin.add_view(SubscriptionPlanAdmin)
    admin.add_view(TenantSubscriptionAdmin)
    admin.add_view(AddonProductAdmin)
    admin.add_view(TenantAddonAdmin)
    
    return admin
