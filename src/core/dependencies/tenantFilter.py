# src/database/tenant_filter.py
from sqlalchemy import event
from sqlalchemy.orm import Session, with_loader_criteria
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.dependencies.context import get_current_tenant_id

def register_tenant_filter(session: AsyncSession) -> None:
    """
    Attach a listener to this session that automatically appends
    WHERE tenant_id = <current> to every ORM query on TenantMixin models.
    """
    @event.listens_for(session.sync_session, "do_orm_execute")
    def _apply_tenant_filter(execute_state):
        # Only intercept SELECT statements, not INSERT/UPDATE/DELETE
        if not execute_state.is_select:
            return

        # Skip if explicitly opted out (for admin/cross-tenant queries)
        if execute_state.execution_options.get("skip_tenant_filter", False):
            return

        tenant_id = get_current_tenant_id()
        if tenant_id is None:
            return  # unauthenticated or system context — let it pass

        # Apply filter to every entity in the query that has tenant_id
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

def _collect_tenant_entities(execute_state) -> list:
    """Extract all mapped entities in the query that use TenantMixin."""
    from sqlalchemy.orm import with_loader_criteria  # local to avoid circular
    entities = []
    for mapper in execute_state.statement.column_descriptions:
        entity = mapper.get("entity")
        if entity is not None and issubclass(entity, TenantMixin):
            entities.append(entity)
    return entities