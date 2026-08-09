from sqlalchemy import event, inspect
from sqlalchemy.orm import Session, RelationshipProperty
from src.core.dependencies.context import get_current_actor_id, get_current_staff_id
from src.database.base import BaseFields
from src.repository.audit.auditLog_model import AuditLogs
from enum import Enum

def _unwrap(value):
    """Return the primitive value for enums, str for everything else."""
    if isinstance(value, Enum):
        return str(value.value)
    return str(value) if value is not None else None

def register_audit_listener():
    """Call once during app startup — not at import time."""

    @event.listens_for(Session, "before_flush")
    def receive_before_flush(session, flush_context, instances):
        actor_id = get_current_actor_id()
        staff_id = get_current_staff_id()

        for obj in session.new:
            if isinstance(obj, BaseFields) and obj.created_by_actor_id is None:
                obj.created_by_actor_id = actor_id

        audits = []
        for obj in session.dirty:
            if not isinstance(obj, BaseFields):
                continue
            instance_state = inspect(obj)
            mapper = inspect(type(obj))
            for attr in instance_state.attrs:
                prop = mapper.attrs.get(attr.key)
                if prop is None or isinstance(prop, RelationshipProperty):
                    continue
                history = attr.history
                if history.has_changes():
                    audits.append(AuditLogs(
                        table_name=obj.__tablename__,
                        record_id=obj.id,
                        action="UPDATE",
                        field_name=attr.key,
                        old_value=_unwrap(history.deleted[0]) if history.deleted else None,
                        new_value=_unwrap(history.added[0]) if history.added else None,
                        changed_by=staff_id,
                    ))

        for obj in session.deleted:
            if not isinstance(obj, BaseFields):
                continue
            audits.append(AuditLogs(
                table_name=obj.__tablename__,
                record_id=obj.id,
                action="DELETE",
                field_name=None,
                old_value=None,
                new_value=None,
                changed_by=staff_id,
            ))
        
        for audit in audits:
            session.add(audit)