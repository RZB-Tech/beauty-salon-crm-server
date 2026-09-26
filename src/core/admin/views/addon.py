from sqladmin import ModelView
from wtforms import SelectField

from src.repository.tenant.subscription.subscriptionPlan_model import AddonProduct, TenantAddon
from src.services.system.tenantLimits_service import TenantLimit

_LIMIT_KEY_CHOICES = [(limit.value, limit.value) for limit in TenantLimit]

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
