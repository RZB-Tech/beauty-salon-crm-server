from functools import wraps
from fastapi import HTTPException, status
from pydantic import BaseModel

_NOT_FOUND_MESSAGES_RU = {
    "employees": "Сотрудник с ID {id} не найден",
    "absences": "Отсутствие с ID {id} не найдено",
    "clients": "Клиент с ID {id} не найден",
    "appointments": "Посещение с ID {id} не найдено",
}

def require_exists(repo_attr: str, target_param: str = "id"):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            entity_id = None
            found_param = False

            # 1. Look in keyword arguments
            if target_param in kwargs:
                entity_id = kwargs[target_param]
                found_param = True
            
            # 2. Look inside Pydantic schemas
            else:
                for arg in args + tuple(kwargs.values()):
                    if isinstance(arg, BaseModel) and hasattr(arg, target_param):
                        entity_id = getattr(arg, target_param)
                        found_param = True
                        break

            # 3. Look by positional index
            if not found_param:
                import inspect
                sig = inspect.signature(func)
                if target_param in sig.parameters:
                    param_names = list(sig.parameters.keys())
                    param_index = list(sig.parameters.keys()).index(target_param)
                    
                    if "self" in param_names:
                        param_index -= 1

                    if param_index < len(args):
                        entity_id = args[param_index]
                        found_param = True

            if not found_param:
                raise ValueError(f"Не удалось найти параметр '{target_param}' в {func.__name__}")

            # 👉 CRITICAL ADDITION FOR OPTIONAL FIELDS: 
            # If the field is allowed to be None and IS None, skip DB validation safely.
            if entity_id is None:
                return await func(self, *args, **kwargs)

            # 4. Database execution
            repo = getattr(self.uow, repo_attr)
            check = await repo.get(entity_id)
            if not check:
                message = _NOT_FOUND_MESSAGES_RU.get(repo_attr, "Объект с ID {id} не найден")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=message.format(id=entity_id)
                )

            return await func(self, *args, **kwargs)
        return wrapper
    return decorator