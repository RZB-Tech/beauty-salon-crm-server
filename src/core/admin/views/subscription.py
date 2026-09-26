from sqladmin import ModelView
from starlette.requests import Request
from wtforms import SelectField

from src.core.cache.tenant_cache import delete_tenant_active
from src.repository.tenant.subscription.subscriptionPlan_model import SubscriptionPlan
from src.repository.tenant.tenant_model import TenantSubscriptions, TenantSubscriptionStatus

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
        SubscriptionPlan.max_users, SubscriptionPlan.max_clients, SubscriptionPlan.can_create_branches,
        SubscriptionPlan.is_visible, SubscriptionPlan.archived,
    ]
    column_details_list = [
        SubscriptionPlan.id, SubscriptionPlan.name, SubscriptionPlan.description,
        SubscriptionPlan.price, SubscriptionPlan.duration_days,
        SubscriptionPlan.max_users, SubscriptionPlan.max_clients, SubscriptionPlan.can_create_branches,
        SubscriptionPlan.is_visible, SubscriptionPlan.archived,
    ]
    column_sortable_list = [SubscriptionPlan.id, SubscriptionPlan.name, SubscriptionPlan.price]
    column_searchable_list = [SubscriptionPlan.name]

    form_columns = [
        SubscriptionPlan.name, SubscriptionPlan.description, SubscriptionPlan.price, SubscriptionPlan.duration_days,
        SubscriptionPlan.max_users, SubscriptionPlan.max_clients, SubscriptionPlan.can_create_branches,
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
