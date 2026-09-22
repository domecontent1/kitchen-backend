# backend/app/core/indexes.py
from app.core.database import database


async def create_indexes():
    await database["users"].create_index("phone", unique=True)

    await database["addresses"].create_index([
        ("user_id", 1),
        ("active", 1),
        ("created_at", -1)
    ])

    await database["orders"].create_index(
        [("customer_id", 1), ("idempotency_key", 1)],
        unique=True,
        partialFilterExpression={"idempotency_key": {"$type": "string"}})

    await database["orders"].create_index(
        [("customer_id", 1), ("created_at", -1)])

    await database["orders"].create_index([("created_at", -1)])

    await database["dishes"].create_index(
        [("active", 1), ("created_at", -1)])

    await database["notifications"].create_index(
        [("user_id", 1), ("created_at", -1)])

    await database["notifications"].create_index(
        [("user_id", 1), ("read", 1)])