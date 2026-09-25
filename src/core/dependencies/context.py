from contextlib import contextmanager
from contextvars import ContextVar

_current_staff_id: ContextVar[int | None] = ContextVar("current_staff_id", default=None)
_current_tenant_id: ContextVar[int | None] = ContextVar("current_tenant_id", default = None)
_current_actor_id: ContextVar[int | None] = ContextVar("current_actor_id", default = None)

def set_current_staff_id(staff_id: int, tenant_id: int, actor_id: int) -> None:
    _current_staff_id.set(staff_id)
    _current_tenant_id.set(tenant_id)
    _current_actor_id.set(actor_id)

def get_current_staff_id() -> int | None:
    return _current_staff_id.get()

def get_current_tenant_id() -> int | None:
    return _current_tenant_id.get()

def get_current_actor_id() -> int | None:
    return _current_actor_id.get()

@contextmanager
def tenant_context(tenant_id: int, actor_id: int | None):
    """
    Temporarily acts on behalf of a tenant outside a staff request (the Telegram
    mini app has no staff token) - the tenant filter and audit listener then
    scope/stamp rows exactly as for that tenant's own staff. Flush inside the
    block: a flush that happens after it exits sees no tenant/actor.
    """
    tenant_token = _current_tenant_id.set(tenant_id)
    actor_token = _current_actor_id.set(actor_id)
    try:
        yield
    finally:
        _current_actor_id.reset(actor_token)
        _current_tenant_id.reset(tenant_token)

@contextmanager
def cleared_actor_context():
    """
    Temporarily clears the current actor context.

    Use around writes that belong to a different tenant than the caller's own
    actor (e.g. provisioning a branch tenant's rows) - otherwise the global
    audit listener stamps created_by_actor_id with the caller's actor_id,
    which violates the (actor_id, tenant_id) composite FK on BaseFields rows
    belonging to the other tenant.
    """
    token = _current_actor_id.set(None)
    try:
        yield
    finally:
        _current_actor_id.reset(token)