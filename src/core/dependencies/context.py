from contextvars import ContextVar

_current_staff_id: ContextVar[int | None] = ContextVar("current_staff_id", default=None)

def set_current_staff_id(staff_id: int) -> None:
    _current_staff_id.set(staff_id)

def get_current_staff_id() -> int | None:
    return _current_staff_id.get()