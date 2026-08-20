import secrets
import string

from src.core.auth.security import hash_password
from src.core.dependencies.context import cleared_actor_context, get_current_actor_id, get_current_tenant_id
from src.core.dependencies.uow import UnitOfWork
from src.database.session import SessionLocal
from src.exceptions.staff_exceptions import StaffNotFound, StaffTenantConflict
from src.exceptions.tenant_exceptions import BranchDoesNotBelongToTenant, TenantNotFound
from src.repository.staff.staff_model import Staff
from src.repository.tenant.tenant_model import Tenant
from src.schemas.tenant.create import TenantBranchCreateSchema
from src.schemas.tenant.update import UpdateBranchAdminPassword
from src.services.system.tenant_service import provision_tenant
from sqlalchemy import select, update

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

        creator_actor_id = get_current_actor_id()

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
                    created_by_actor_id = creator_actor_id,
                )
                await session.commit()
        return result

    async def get_all(self) -> list[Tenant]:
        tenant = await self._get_current_tenant_or_raise()
        return await self.uow.tenants.get_branches(tenant.id)

    async def reset_admin_password(self, data: UpdateBranchAdminPassword) -> str | None:
        """
        Resets / update admin's password\n
        If provided `password` - set hashed password and return None\n
        If `password` has not provided - generate random password, set hashed and return
        """
        parentTenant = await self._get_current_tenant_or_raise()
        tenant = await self.uow.tenants.get(id = data.branch_id)
        if tenant is None: raise TenantNotFound(data.branch_id)
        if tenant.parent_id != parentTenant.id: raise BranchDoesNotBelongToTenant(parentTenant.id, data.branch_id)

        result = await self.uow.db.execute(
            select(Staff)
            .where(Staff.id == data.admin_id)
            .execution_options(skip_tenant_filter = True)
        )
        admin = result.scalar_one_or_none()
        if admin is None: raise StaffNotFound()
        if admin.tenant_id != tenant.id: raise StaffTenantConflict(data.admin_id, data.branch_id)

        plainPassword: str
        if data.password is not None: plainPassword = data.password
        else:
            alphabet = (
                string.ascii_letters +
                string.digits +
                "!@#$%^&*-_=+?"
            )

            plainPassword = "".join(secrets.choice(alphabet) for _ in range(16))
        hashed = hash_password(plainPassword)

        async with SessionLocal() as session:
            await session.execute(
                update(Staff)
                .where(Staff.id == data.admin_id)
                .values(hashed_password = hashed)
            )
            await session.commit()

        return plainPassword if data.password is None else None