import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.database.base import BaseFields
from src.core.dependencies.dbContext import set_db_context
from src.database.context import db_session_ctx
from src.app import app

ADMIN_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5450/postgres"
TEST_DB_NAME = "salon_test"
TEST_DATABASE_URL = f"postgresql+asyncpg://postgres:postgres@localhost:5450/{TEST_DB_NAME}"

# We will instantiate this test engine inside our fixture once the DB exists
test_engine = create_async_engine(TEST_DATABASE_URL, poolclass = NullPool)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=test_engine, expire_on_commit = False)

async def override_get_db():
    async with TestingSessionLocal() as session:
        token = db_session_ctx.set(session)
        try:
            yield session
        finally:
            db_session_ctx.reset(token)

app.dependency_overrides[set_db_context] = override_get_db

# 2. Database Creation & Destruction
@pytest_asyncio.fixture(scope="session", loop_scope = "session", autouse=True)
async def prepare_database():
    """Dynamically creates and destroys the PostgreSQL database for the test session."""
    
    # isolation_level="AUTOCOMMIT" is required to run CREATE/DROP DATABASE
    admin_engine = create_async_engine(ADMIN_DATABASE_URL, isolation_level="AUTOCOMMIT")

    async with admin_engine.connect() as conn:
        # Check if leftover database exists from a previous crashed run
        result = await conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{TEST_DB_NAME}'"))
        if result.scalar():
            # Kick off any lingering connections, then drop
            await conn.execute(text(f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{TEST_DB_NAME}'"))
            await conn.execute(text(f"DROP DATABASE {TEST_DB_NAME}"))
        
        # Create the fresh test database
        await conn.execute(text(f"CREATE DATABASE {TEST_DB_NAME}"))
    
    await admin_engine.dispose()

    # Now that the DB exists, create the tables
    async with test_engine.begin() as conn:
        await conn.run_sync(BaseFields.metadata.create_all)

    yield # <--- YOUR TESTS RUN HERE

    # Teardown: Disconnect the test engine
    await test_engine.dispose()

    # Reconnect as admin to drop the database cleanly
    admin_engine = create_async_engine(ADMIN_DATABASE_URL, isolation_level="AUTOCOMMIT")
    async with admin_engine.connect() as conn:
        await conn.execute(text(f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{TEST_DB_NAME}'"))
        await conn.execute(text(f"DROP DATABASE {TEST_DB_NAME}"))
    await admin_engine.dispose()

@pytest_asyncio.fixture
async def db_session():
    """Provides a dedicated database session for seeding data inside a test.
    Automatically cleans up all data after the test completes."""
    async with TestingSessionLocal() as session:
        yield session
        # Clean up any uncommitted lingering changes inside this specific session
        await session.rollback()

    # CRITICAL FOR ISOLATION: Wipe data from all tables after the test runs.
    # This prevents Test A's client from breaking unique constraints in Test B.
    async with test_engine.begin() as conn:
        # Disable foreign key checks temporarily during truncate or use CASCADE
        for table in reversed(BaseFields.metadata.sorted_tables):
            await conn.execute(text(f"TRUNCATE TABLE {table.name} RESTART IDENTITY CASCADE;"))

# 3. HTTP Client
@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client