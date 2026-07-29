import json

from markupsafe import Markup
from sqladmin import BaseView, ModelView, expose
from sqlalchemy.exc import IntegrityError
from starlette.requests import Request

from src.core.cache.tenant_cache import delete_tenant_active
from src.database.session import SessionLocal
from src.repository.tenant.tenant_model import Tenant
from src.services.system.tenant_service import provision_tenant

def _format_preferences(model: Tenant, attribute: str) -> Markup:
    value = getattr(model, attribute)
    if not value:
        return Markup("—")
    pretty = json.dumps(value, indent = 2, ensure_ascii = False, sort_keys = True)
    return Markup("<pre class='mb-0'>{}</pre>").format(pretty)

def _format_integration(model: Tenant, attribute: str) -> str:
    integration = getattr(model, attribute)
    if integration is None:
        return "—"
    return "Telegram: настроен" if integration.telegram_bot_token else "Telegram: не настроен"

class TenantAdmin(ModelView, model = Tenant):
    name = "Тенант"
    name_plural = "Тенанты"
    category = "Тенанты"
    icon = "fa-solid fa-building"

    can_create = False
    can_edit = True
    can_delete = False
    can_view_details = True

    column_list = [Tenant.id, Tenant.name, Tenant.TIN, Tenant.created_at, Tenant.active]
    column_details_list = [
        Tenant.id, Tenant.name, Tenant.TIN, Tenant.active,
        Tenant.preferences, Tenant.integration,
        Tenant.created_at, Tenant.updated_at,
    ]
    column_sortable_list = [Tenant.id, Tenant.name, Tenant.created_at, Tenant.active]
    column_searchable_list = [Tenant.name, Tenant.TIN]

    column_formatters_detail = {
        Tenant.preferences: _format_preferences,
        Tenant.integration: _format_integration,
    }
    non_link_related_fields = [Tenant.integration]

    form_columns = [Tenant.name, Tenant.TIN, Tenant.active]

    async def after_model_change(self, data: dict, model: Tenant, is_created: bool, request: Request) -> None:
        await delete_tenant_active(model.id)

class TenantCreateView(BaseView):
    name = "Создать тенанта"
    category = "Тенанты"
    identity = "tenant-create"
    icon = "fa-solid fa-plus"

    @expose("/tenant-create", methods = ["GET", "POST"], identity = "tenant-create")
    async def tenant_create(self, request: Request):
        context: dict = {}

        if request.method == "POST":
            form = await request.form()
            company_name = str(form.get("company_name") or "").strip()
            company_tin = str(form.get("company_tin") or "").strip() or None
            admin_firstname = str(form.get("admin_firstname") or "").strip()
            admin_login = str(form.get("admin_login") or "").strip()
            admin_password = str(form.get("admin_password") or "").strip() or None

            if not company_name or not admin_firstname or not admin_login:
                context["error"] = "Заполните обязательные поля."
            else:
                try:
                    async with SessionLocal() as session:
                        result = await provision_tenant(
                            db = session,
                            company_name = company_name,
                            company_tin = company_tin,
                            admin_login = admin_login,
                            admin_firstname = admin_firstname,
                            admin_password = admin_password,
                        )
                        await session.commit()
                    context["result"] = result
                except IntegrityError:
                    context["error"] = "Тенант с таким названием или логин администратора уже существуют."

        return await self.templates.TemplateResponse(request, "tenant_create.html", context)
