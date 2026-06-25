# src/database/tenant_filter.py
from sqlalchemy import event
import sqlalchemy
from sqlalchemy.orm import with_loader_criteria
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.dependencies.context import get_current_tenant_id
from src.database.mixins import TenantMixin

def register_tenant_filter(session: AsyncSession) -> None:
    """
    Attach a listener to this session that automatically isolates
    SELECT, UPDATE, and DELETE actions to the active tenant_id context.
    """
    @event.listens_for(session.sync_session, "do_orm_execute")
    def _apply_tenant_filter(execute_state):
        # Skip if explicitly opted out (for cross-tenant admin operations)
        if execute_state.execution_options.get("skip_tenant_filter", False):
            return

        tenant_id = get_current_tenant_id()
        if tenant_id is None:
            # Secure by default: If we cannot find a tenant context during an active
            # client request state, we should block modification statements entirely.
            if execute_state.is_delete or execute_state.is_update:
                raise PermissionError("Database mutation attempted without a valid tenant context.")
            return  

        # Apply isolation filter dynamically to SELECT, UPDATE, and DELETE operations
        execute_state.statement = execute_state.statement.options(
            *[
                with_loader_criteria(
                    entity_cls,
                    lambda alias, tid=tenant_id: alias.tenant_id == tid,
                    include_aliases=True,
                )
                for entity_cls in _collect_tenant_entities(execute_state)
            ]
        )

    @event.listens_for(session.sync_session, "before_flush")
    def _evict_or_inject_tenant_id(sync_session, flush_context, instances):
        tenant_id = get_current_tenant_id()
        if tenant_id is None:
            return  

        # Handle Inserts (session.new)
        for obj in sync_session.new:
            if hasattr(obj, "tenant_id"):
                if getattr(obj, "tenant_id") is None:
                    setattr(obj, "tenant_id", tenant_id)
                elif getattr(obj, "tenant_id") != tenant_id:
                    raise PermissionError("Cross-tenant data injection detected!")

        # Handle Updates (session.dirty)
        for obj in sync_session.dirty:
            if hasattr(obj, "tenant_id"):
                if sync_session.is_modified(obj, include_collections=False):
                    state = sqlalchemy.inspect(obj)
                    history = state.get_history("tenant_id", passive=True)
                    if history.has_changes():
                        raise PermissionError("Altering the tenant_id of an existing record is prohibited.")

        # Handle Deletes (session.deleted) - Ensure instance tenant validation
        for obj in sync_session.deleted:
            if hasattr(obj, "tenant_id"):
                if getattr(obj, "tenant_id") != tenant_id:
                    raise PermissionError("Unauthorized attempt to delete cross-tenant records.")

def _collect_tenant_entities(execute_state) -> list:
    """Extract all mapped entities in the query that use TenantMixin."""
    from sqlalchemy.orm import with_loader_criteria  # local to avoid circular
    entities = []
    for mapper in execute_state.statement.column_descriptions:
        entity = mapper.get("entity")
        if entity is not None and issubclass(entity, TenantMixin):
            entities.append(entity)
    return entities