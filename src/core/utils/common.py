from datetime import datetime, timezone
import re

from src.core.dependencies.context import get_current_tenant_id
from src.core.dependencies.uow import UnitOfWork
from src.exceptions.tenant_exceptions import BranchDoesNotBelongToTenant, TenantNotFound
from src.repository.tenant.tenant_model import Tenant

def as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)

def validate_contain_only_alpha_and_digits(value: str) -> bool:
    return False if re.fullmatch(r"[a-zA-Z0-9]+", value) is None else True

async def get_current_tenant_or_raise(uow: UnitOfWork) -> Tenant:
    tenant_id = get_current_tenant_id()
    tenant = await uow.tenants.get(id = tenant_id)
    if tenant is None: raise TenantNotFound(tenant_id)
    return tenant

async def check_branch_belong_to_tenant(uow: UnitOfWork,  
                                        branchID: int,
                                        parentID: int | None = None) -> None:
    """
    If parentID is not provided - parentID will use current context tenant's ID
    """
    parent: Tenant
    if parentID is not None:
        parent = await uow.tenants.get(id = parentID)
        if parent is None: raise TenantNotFound(parentID)
    else: parent = await get_current_tenant_or_raise(uow)

    branch = await uow.tenants.get(id = branchID)
    if branch is None: raise TenantNotFound(branchID)
    if branch.parent_id != parent.id: raise BranchDoesNotBelongToTenant(parent.id, branchID)