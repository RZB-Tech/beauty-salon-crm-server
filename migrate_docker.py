import asyncio
from pathlib import Path
import shutil
import subprocess
import os
from faker import Faker
import random
from datetime import date, time, timedelta, timezone

from src.database.session import SessionLocal
from src.repository.client.client_model import Client, Sex
from src.repository.employee.employee_model import Employee
from src.repository.employee.workSchedule_model import WorkSchedule
from src.repository.material.material_model import Material, MeasurementUnit
from sqlalchemy import select, text

from src.repository.payroll.payroll_model import Payroll, PayrollType

fake = Faker("ru_RU")

DB_NAME = "salon"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "postgres-salon"
DB_PORT = "5432"

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
            await conn.execute(text("DROP TABLE IF EXISTS alembic_version;"))
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
        insert into tenants (name, active, preferences)
        values ('synapse', true, '{
            "theme": "light",
            "timezone": "UTC",
            "currency": "UZS",
            "enable_telegram_booking": false,
            "cancel_payment_due": 0
        }'::jsonb);

        insert into tenants (name, active, preferences)
        values ('rzbtech', true, '{
            "theme": "light",
            "timezone": "UTC",
            "currency": "UZS",
            "enable_telegram_booking": false,
            "cancel_payment_due": 0
        }'::jsonb);

        insert into actors (actor_type, tenant_id)
        values ('staff', 1);

        insert into actors (actor_type, tenant_id)
        values ('staff', 2);

        INSERT INTO staffs
            (firstname, login, tenant_id, staff_type, active, hashed_password, actor_id)
        VALUES
            (
                'max',
                'admin',
                1,
                'administrator',
                true,
                '$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$Eyo2xYv1fdJwRTeT/xFWS3c6SYqZhlYVI9gRUvcUdSc',
                1
            );

        INSERT INTO staffs
            (firstname, login, tenant_id, staff_type, active, hashed_password, actor_id)
        VALUES
            (
                'eva',
                'admin1',
                2,
                'administrator',
                true,
                '$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$Eyo2xYv1fdJwRTeT/xFWS3c6SYqZhlYVI9gRUvcUdSc',
                2
            );

        insert into tenant_integrations
            (tenant_id, telegram_bot_token)
        values
            (1, null);

        insert into tenant_integrations
            (tenant_id, telegram_bot_token)
        values
            (2, null);
        """,
    ])

async def seed_employees(count: int = 10) -> None:
    print(f"Creating {count} employees...")

    async with SessionLocal() as session:
        employees = []

        for _ in range(count):
            employee = Employee(
                firstname=fake.first_name(),
                lastname=fake.last_name(),
                middlename=fake.first_name(),
                phone=fake.phone_number()[:50],
                birth_date=fake.date_of_birth(
                    minimum_age=18,
                    maximum_age=65,
                ),
                active=random.choice([True, True, True, False]),
                salary_fixed=random.randint(
                    3_000_000,
                    15_000_000,
                ),
                percent_from_services=random.randint(5, 30),
                percent_from_sales=random.randint(0, 15),
                notes=fake.text(max_nb_chars=100),
                created_by_actor_id = 1,
                tenant_id = 1
            )

            employees.append(employee)

        session.add_all(employees)
        await session.commit()

async def seed_clients(count: int = 100) -> None:
    print(f"Creating {count} clients...")

    async with SessionLocal() as session:
        clients = []

        for _ in range(count):
            client = Client(
                firstname=fake.first_name(),
                lastname=fake.last_name(),
                middlename=fake.first_name(),
                phone=fake.phone_number()[:50],
                birth_date=fake.date_of_birth(
                    minimum_age=18,
                    maximum_age=80,
                ),
                sex=random.choice([
                    Sex.MALE,
                    Sex.FEMALE,
                ]),
                notes=fake.text(max_nb_chars=100),
                deposit=random.randint(0, 1_000_000),
                created_by_actor_id = 1,
                tenant_id = 1
            )

            clients.append(client)

        session.add_all(clients)
        await session.commit()

async def seed_materials(count: int = 100) -> None:
    print(f"Creating {count} materials...")

    async with SessionLocal() as session:
        materials = []

        material_names = [
            "Shampoo",
            "Hair Color",
            "Hair Mask",
            "Conditioner",
            "Hair Spray",
            "Nail Polish",
            "Gel",
            "Cream",
            "Oil",
            "Serum",
            "Wax",
            "Disposable Gloves",
            "Foil",
            "Cotton Pads",
            "Towel",
        ]

        for i in range(count):
            purchase_price = random.randint(10_000, 200_000)

            material = Material(
                article=f"MAT-{fake.unique.random_int(10000, 99999)}",

                name=f"{random.choice(material_names)} {fake.word()}",

                description=fake.text(max_nb_chars=100),

                quantity=random.randint(0, 500),

                measurement_unit=random.choice([
                    MeasurementUnit.PCS,
                    MeasurementUnit.KG,
                    MeasurementUnit.L,
                    MeasurementUnit.GR,
                ]),

                volume=random.randint(1, 1000),

                sell_price=purchase_price + random.randint(
                    20_000,
                    100_000
                ),
                created_by_actor_id = 1,
                tenant_id = 1
            )

            materials.append(material)

        session.add_all(materials)
        await session.commit()
        
UZT = timezone(timedelta(hours = 5))

async def seed_work_schedules() -> None:
    print("Creating employee work schedules...")

    async with SessionLocal() as session:
        employees = await session.scalars(
            select(Employee)
        )

        employees = employees.all()

        schedules = []

        # Create schedule for next 30 days
        today = date.today()

        for employee in employees:
            for day_offset in range(30):
                current_day = today + timedelta(days=day_offset)

                # Skip some weekends randomly
                if current_day.weekday() >= 5:
                    if fake.boolean(chance_of_getting_true=70):
                        continue

                start_hour = fake.random_element([
                    9,
                    10,
                    11,
                ])

                start_time = time(
                    hour=start_hour,
                    minute=0,
                    tzinfo = UZT
                )

                end_time = time(
                    hour=start_hour + 8,
                    minute=0,
                    tzinfo = UZT
                )

                schedules.append(
                    WorkSchedule(
                        employee_id=employee.id,
                        day=current_day,
                        start_time=start_time,
                        end_time=end_time,
                        created_by_actor_id = 1,
                        tenant_id = 1
                    )
                )

        session.add_all(schedules)
        await session.commit()

    print(f"Created {len(schedules)} work schedules")

async def seed_payrolls(count_per_employee: int = 3) -> None:
    print("Creating payroll records...")

    async with SessionLocal() as session:
        employees = await session.scalars(
            select(Employee)
        )

        employees = employees.all()

        payrolls = []

        for employee in employees:
            for _ in range(count_per_employee):

                payroll_type = random.choice([
                    PayrollType.BONUS,
                    PayrollType.COMMISSION,
                    PayrollType.PENALTY,
                ])

                if payroll_type == PayrollType.BONUS:
                    amount = random.randint(
                        100_000,
                        2_000_000
                    )
                    note = fake.sentence()

                elif payroll_type == PayrollType.COMMISSION:
                    amount = random.randint(
                        50_000,
                        1_000_000
                    )
                    note = "Service commission"

                else:
                    amount = random.randint(
                        50_000,
                        500_000
                    )
                    note = "Penalty"

                payrolls.append(
                    Payroll(
                        employee_id=employee.id,
                        amount=amount,
                        type=payroll_type,
                        notes=note,
                        created_by_actor_id = 1,
                        tenant_id = 1
                    )
                )

        session.add_all(payrolls)
        await session.commit()

    print(f"Created {len(payrolls)} payroll records")

async def main():
    drop_database()
    create_database()
    await delete_migrations()
    create_migration()
    apply_migrations()
    seed_admin_user()
    await seed_employees()
    await seed_clients()
    await seed_materials()
    # await seed_work_schedules()
    await seed_payrolls()

    print("Done.")

if __name__ == "__main__":
    asyncio.run(main())