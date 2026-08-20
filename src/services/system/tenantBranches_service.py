from src.core.dependencies.context import cleared_actor_context, get_current_tenant_id
from src.core.dependencies.uow import UnitOfWork
from src.database.session import SessionLocal
from src.exceptions.tenant_exceptions import TenantCannotCreateBranch, TenantNotFound
from src.repository.tenant.tenant_model import Tenant
from src.schemas.tenant.create import TenantBranchCreateSchema
from src.services.system.tenant_service import provision_tenant

class TenantBranchesService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def _get_current_tenant_or_raise(self) -> Tenant:
        tenant_id = get_current_tenant_id()
        tenant = await self.uow.tenants.get(id = tenant_id)
        if tenant is None: raise TenantNotFound(tenant_id)
        return tenant

    async def create(self, data: TenantBranchCreateSchema) -> dict:
        tenant = await self._get_current_tenant_or_raise()
        if tenant.parent_id is not None: raise TenantCannotCreateBranch()

        # provision_tenant writes rows tagged with the new branch's tenant_id, which the
        # request's tenant-scoped session (self.uow.db) would reject as cross-tenant data
        # injection (src/core/dependencies/tenantFilter.py). Use a standalone session
        # without that filter attached, same as sqladmin's TenantCreateView does.
        async with SessionLocal() as session:
            with cleared_actor_context():
                result = await provision_tenant(
                    session,
                    company_name = data.company_name,
                    company_tin = data.company_tin,
                    admin_login = data.admin_login,
                    admin_firstname = data.admin_firstname,
                    admin_password = data.admin_password,
                    parent_id = tenant.id,
                )
                await session.commit()
        return result

    async def get_all(self) -> list[Tenant]:
        tenant = await self._get_current_tenant_or_raise()
        return await self.uow.tenants.get_branches(tenant.id)
