# import asyncio
# from datetime import datetime, timedelta

# from sqlalchemy import insert
# from sqlalchemy.exc import SQLAlchemyError
# from src.database.session import SessionLocal
# from src.repository.transaction.transaction_model import Transaction, TransactionCategory, TransactionMethod, TransactionType
# import random
# DB_NAME = "salon"
# DB_USER = "postgres"
# DB_PASSWORD = "postgres"
# DB_HOST = "localhost"
# DB_PORT = "5450"

# async def add_one(session, obj) -> bool:
#     session.add(obj)

#     try:
#         await session.commit()
#         return True
#     except SQLAlchemyError as e:
#         await session.rollback()
#         print(f"Skipping duplicate/invalid record ({obj.__class__.__name__}): {e}")
#         return False

# def random_datetime(year_start: int, year_end: int) -> datetime:
#     start = datetime(year_start, 1, 1)
#     end = datetime(year_end, 12, 31, 23, 59, 59)
#     delta = end - start
#     random_seconds = random.randint(0, int(delta.total_seconds()))
#     return start + timedelta(seconds=random_seconds)

# async def seed_transactions(count: int = 10) -> None:
#     print(f"Creating {count} transactions...")
#     created = 0
#     tTypes = list(TransactionType)
#     tMethods = list(TransactionMethod)
#     tCategories = list(TransactionCategory)

#     async with SessionLocal() as session:
#         for _ in range(count):
#             stmt = insert(Transaction).values(
#                 amount=random.randint(1, 10_000_000),
#                 type=random.choice(tTypes),
#                 method=random.choice(tMethods),
#                 category=random.choice(tCategories),
#                 auto_generated=True,
#                 created_at=random_datetime(2020, 2026),
#                 created_by_actor_id=1,
#                 tenant_id=1,
#             )
#             try:
#                 await session.execute(stmt)
#                 await session.commit()
#                 created += 1
#             except SQLAlchemyError as e:
#                 await session.rollback()
#                 print(f"Skipping invalid record: {e}")

#     print(f"Created {created} transactions")

# asyncio.run(seed_transactions(100000))

from datetime import datetime
a = datetime(2026, 8, 28)
b = datetime(2026, 9, 1)
print(a.isocalendar().week)
print(b.isocalendar().week)