import asyncio
import os
import subprocess
import sys

DB_NAME = "salon_test"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = "5450"

# Construct standard URLs for both synchronous (Alembic/psql) and asynchronous (FastAPI/asyncpg) drivers
ASYNC_DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
SYNC_DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def run(cmd: list[str], extra_env: dict = None) -> None:
    env = os.environ.copy()
    env["PGPASSWORD"] = DB_PASSWORD
    # 💡 Force the database URL into the environment so Alembic/FastAPI target the test DB
    env["DATABASE_URL"] = ASYNC_DB_URL  
    
    if extra_env:
        env.update(extra_env)

    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True, env=env)

def drop_database() -> None:
    print(f"Dropping database '{DB_NAME}'...")
    run([
        "dropdb",
        "--force",
        "-h", DB_HOST,
        "-p", DB_PORT,
        "-U", DB_USER,
        "--if-exists",
        DB_NAME,
    ])

def create_database() -> None:
    print(f"Creating database '{DB_NAME}'...")
    run([
        "createdb",
        "-h", DB_HOST,
        "-p", DB_PORT,
        "-U", DB_USER,
        DB_NAME,
    ])

def apply_migrations() -> None:
    print("Applying migrations...")
    # Pass the synchronous URL to Alembic if your alembic env.py expects it,
    # or let it fall back to the default ASYNC_DB_URL env variable.
    run(["alembic", "upgrade", "head"])

def seed_admin_user() -> None:
    print("Creating admin user...")
    run([
        "psql",
        "-h", DB_HOST,
        "-p", DB_PORT,
        "-U", DB_USER,
        "-d", DB_NAME,
        "-c",
        """
        insert into tenants (name, active) values ('synapse', true);
        insert into tenants (name, active) values ('rzbtech', true);
        insert into actors (actor_type, tenant_id) values ('staff', 1);
        insert into actors (actor_type, tenant_id) values ('staff', 2);

        INSERT INTO staffs
            (firstname, login, tenant_id, staff_type, active, hashed_password, actor_id)
        VALUES
            ('max', 'admin', 1, 'administrator', true, '$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$Eyo2xYv1fdJwRTeT/xFWS3c6SYqZhlYVI9gRUvcUdSc', 1),
            ('eva', 'admin1', 2, 'administrator', true, '$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$Eyo2xYv1fdJwRTeT/xFWS3c6SYqZhlYVI9gRUvcUdSc', 2);

        insert into tenant_integrations (tenant_id, telegram_bot_token) values (1, null), (2, null);
        """,
    ])

async def main():
    # 1. Clean build environment
    drop_database()
    create_database()
    
    try:
        # 2. Prepare schema and data
        apply_migrations()
        seed_admin_user()
        print("✅ Environment ready. Running tests...")

        # 3. RUN TESTS
        # This will execute pytest and stream output directly to your terminal.
        # We pass the DATABASE_URL environment variable down so your app loads the test DB context.
        pytestArgs = sys.argv[1:] if len(sys.argv) > 1 else ["-v"]
        run(["uv", "run", "pytest", *pytestArgs])
        
    except subprocess.CalledProcessError:
        print("❌ Tests failed or setup crashed.")
        sys.exit(1)
        
    finally:
        # 4. GUARANTEED CLEANUP
        # Runs whether tests passed, failed, or the user hit Ctrl+C
        drop_database()
        print("🧹 Cleaned up test database.")

if __name__ == "__main__":
    asyncio.run(main())