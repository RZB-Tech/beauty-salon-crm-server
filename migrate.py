import asyncio
from pathlib import Path
import shutil
import subprocess
import os

from sqlalchemy import text
from src.database.session import SessionLocal
from dotenv import load_dotenv
load_dotenv()

DB_NAME = "salon"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = "5450"

VERSIONS_DIR = Path("src/database/alembic/versions")

def run(cmd: list[str]) -> None:
    env = os.environ.copy()
    env["PGPASSWORD"] = DB_PASSWORD

    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True, env=env)


async def delete_migrations() -> None:
    print("Deleting Alembic migration files...")

    for item in VERSIONS_DIR.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    print("Clearing alembic_version table...")
    try:
        async with SessionLocal.begin() as conn:
            await conn.execute(text("DELETE FROM alembic_version"))
            print("Deleted alembic_version rows")
    except Exception as e:
        print(f"Failed to clear alembic_version: {e}")
        raise


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

def create_migration() -> None:
    run([
        "alembic",
        "revision",
        "--autogenerate"
    ])


def apply_migrations() -> None:
    print("Applying migrations...")

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
        insert into tenants (name, active)
        values ('synapse', true);

        INSERT INTO staffs
            (firstname, login, tenant_id, staff_type, active, hashed_password)
        VALUES
            (
                'max',
                'admin',
                1,
                'administrator',
                true,
                '$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$Eyo2xYv1fdJwRTeT/xFWS3c6SYqZhlYVI9gRUvcUdSc'
            );
        """,
    ])


if __name__ == "__main__":
    asyncio.run(delete_migrations())
    drop_database()
    create_database()
    create_migration()
    apply_migrations()
    seed_admin_user()
    print("Done.")