import json

from markupsafe import Markup
from sqladmin import BaseView, ModelView, expose
from sqlalchemy.exc import IntegrityError
from starlette.requests import Request
from wtforms import SelectField

from src.core.cache.tenant_cache import delete_tenant_active, delete_tenant_admin_active
from src.database.session import SessionLocal
from src.repository.tenant.subscription.subscriptionPlan_model import AddonProduct, SubscriptionPlan, TenantAddon
from src.repository.tenant.tenant_model import Tenant, TenantSubscriptions, TenantSubscriptionStatus
from src.services.system.tenantLimits_service import TenantLimit
from src.services.system.tenant_service import provision_tenant

_LIMIT_KEY_CHOICES = [(limit.value, limit.value) for limit in TenantLimit]

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

    column_list = [Tenant.id, Tenant.name, Tenant.TIN, Tenant.parent_id, Tenant.created_at, Tenant.active]
    column_details_list = [
        Tenant.id, Tenant.name, Tenant.TIN, Tenant.parent_id, Tenant.active,
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
        await delete_tenant_admin_active(model.id)

class SubscriptionPlanAdmin(ModelView, model = SubscriptionPlan):
    name = "Тарифный план"
    name_plural = "Тарифные планы"
    category = "Тенанты"
    icon = "fa-solid fa-tags"

    can_create = True
    can_edit = True
    # Plans are referenced by tenant_subscriptions (ondelete=restrict) and by
    # past expenses - retire a plan with `archived` instead of deleting it.
    can_delete = False
    can_view_details = True

    column_list = [
        SubscriptionPlan.id, SubscriptionPlan.name, SubscriptionPlan.price, SubscriptionPlan.duration_days,
        SubscriptionPlan.max_users, SubscriptionPlan.max_clients,
        SubscriptionPlan.is_visible, SubscriptionPlan.archived,
    ]
    column_details_list = [
        SubscriptionPlan.id, SubscriptionPlan.name, SubscriptionPlan.description,
        SubscriptionPlan.price, SubscriptionPlan.duration_days,
        SubscriptionPlan.max_users, SubscriptionPlan.max_clients,
        SubscriptionPlan.is_visible, SubscriptionPlan.archived,
    ]
    column_sortable_list = [SubscriptionPlan.id, SubscriptionPlan.name, SubscriptionPlan.price]
    column_searchable_list = [SubscriptionPlan.name]

    form_columns = [
        SubscriptionPlan.name, SubscriptionPlan.description, SubscriptionPlan.price, SubscriptionPlan.duration_days,
        SubscriptionPlan.max_users, SubscriptionPlan.max_clients,
        SubscriptionPlan.is_visible, SubscriptionPlan.archived
    ]

class TenantSubscriptionAdmin(ModelView, model = TenantSubscriptions):
    name = "Tenants subscription"
    name_plural = "Tenants subscription"
    category = "Subsriptions"
    icon = "fa-solid fa-tags"

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    column_list = [
        TenantSubscriptions.id,
        TenantSubscriptions.tenant,
        TenantSubscriptions.plan,
        TenantSubscriptions.status,
        TenantSubscriptions.amount_paid,
        TenantSubscriptions.started_at,
        TenantSubscriptions.period_end
    ]
    column_details_list = [
        TenantSubscriptions.id,
        TenantSubscriptions.tenant,
        TenantSubscriptions.plan,
        TenantSubscriptions.status,
        TenantSubscriptions.amount_paid,
        TenantSubscriptions.started_at,
        TenantSubscriptions.period_end
    ]
    column_sortable_list = [TenantSubscriptions.id, TenantSubscriptions.status, TenantSubscriptions.period_end]

    form_columns = [
        TenantSubscriptions.tenant,
        TenantSubscriptions.plan,
        TenantSubscriptions.status,
        TenantSubscriptions.amount_paid,
        TenantSubscriptions.started_at,
        TenantSubscriptions.period_end
    ]
    form_ajax_refs = {
        "tenant": {"fields": ("name",)},
        "plan": {"fields": ("name",)},
    }
    form_overrides = {"status": SelectField}
    form_args = {
        "status": {"choices": [(s.value, s.value) for s in TenantSubscriptionStatus]},
    }

    async def after_model_change(self, data: dict, model: TenantSubscriptions, is_created: bool, request: Request) -> None:
        await delete_tenant_active(model.tenant_id)

    async def after_model_delete(self, model: TenantSubscriptions, request: Request) -> None:
        await delete_tenant_active(model.tenant_id)

class AddonProductAdmin(ModelView, model = AddonProduct):
    name = "Аддон (каталог)"
    name_plural = "Аддоны (каталог)"
    category = "Тенанты"
    icon = "fa-solid fa-cart-plus"

    can_create = True
    can_edit = True
    # Referenced by tenant_addons (ondelete=restrict) - retire with `archived`.
    # Editing a product doesn't change addons already bought: purchases copy
    # limit_key and amount.
    can_delete = False
    can_view_details = True

    column_list = [
        AddonProduct.id, AddonProduct.name, AddonProduct.limit_key, AddonProduct.amount,
        AddonProduct.price, AddonProduct.archived,
    ]
    column_details_list = [
        AddonProduct.id, AddonProduct.name, AddonProduct.description, AddonProduct.limit_key,
        AddonProduct.amount, AddonProduct.price, AddonProduct.archived,
        AddonProduct.created_at, AddonProduct.updated_at,
    ]
    column_sortable_list = [AddonProduct.id, AddonProduct.name, AddonProduct.price]
    column_searchable_list = [AddonProduct.name]

    form_columns = [
        AddonProduct.name, AddonProduct.description, AddonProduct.limit_key,
        AddonProduct.amount, AddonProduct.price, AddonProduct.archived,
    ]
    form_overrides = {"limit_key": SelectField}
    form_args = {"limit_key": {"choices": _LIMIT_KEY_CHOICES}}

class TenantAddonAdmin(ModelView, model = TenantAddon):
    name = "Аддон тенанта"
    name_plural = "Аддоны тенантов"
    category = "Тенанты"
    icon = "fa-solid fa-puzzle-piece"

    # Creating here is a free grant: no product, no expense, balance untouched.
    # Limits are per tenant - a grant to a parent doesn't reach its branches.
    can_create = True
    can_edit = True
    # Paid addons are tied to their expense - revoke by setting expires_at in
    # the past instead of deleting.
    can_delete = False
    can_view_details = True

    column_list = [
        TenantAddon.id, TenantAddon.tenant, TenantAddon.limit_key, TenantAddon.amount,
        TenantAddon.product, TenantAddon.expires_at, TenantAddon.created_at,
    ]
    column_details_list = [
        TenantAddon.id, TenantAddon.tenant, TenantAddon.limit_key, TenantAddon.amount,
        TenantAddon.product, TenantAddon.expense_id, TenantAddon.expires_at, TenantAddon.created_at,
    ]
    column_sortable_list = [TenantAddon.id, TenantAddon.limit_key, TenantAddon.created_at]

    form_columns = [TenantAddon.tenant, TenantAddon.limit_key, TenantAddon.amount, TenantAddon.expires_at]
    form_ajax_refs = {"tenant": {"fields": ("name",)}}
    form_overrides = {"limit_key": SelectField}
    form_args = {"limit_key": {"choices": _LIMIT_KEY_CHOICES}}

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
