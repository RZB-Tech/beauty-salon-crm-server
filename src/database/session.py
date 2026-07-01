from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from src.core.config import settings
from contextvars import ContextVar
from src.core.dependencies.tenantFilter import register_tenant_filter

db_session_ctx: ContextVar[AsyncSession | None] = ContextVar("db_session_ctx", default=None)

def get_repository_db() -> AsyncSession:
    session = db_session_ctx.get()
    if session is None:
        raise RuntimeError("Database session has not been initialized for this context.")
    return session

DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=False)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

@asynccontextmanager
async def transaction_scope():
    async with SessionLocal() as session:
        register_tenant_filter(session)
        token = db_session_ctx.set(session)
        try:
            yield session
            await session.commit()
        except Exception as exc:
            await session.rollback()
            raise exc
        finally:
            db_session_ctx.reset(token)

