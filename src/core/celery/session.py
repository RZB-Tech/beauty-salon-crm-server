from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.core.config import settings
from src.database.session import db_session_ctx

@asynccontextmanager
async def celery_transaction_scope():
    """
    Celery workers run outside FastAPI's request lifecycle, so they can't
    reuse the app's shared engine/session context - each task run gets its
    own short-lived engine instead.
    """
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        connect_args={"statement_cache_size": 0},
    )
    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        token = db_session_ctx.set(session)
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            db_session_ctx.reset(token)
            await engine.dispose()
