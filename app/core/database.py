from motor.motor_asyncio import AsyncIOMotorClient

from app.core.settings import settings


if not settings.MONGODB_URL:
    raise RuntimeError(
        "MONGODB_URL is not configured"
    )

if not settings.DATABASE_NAME:
    raise RuntimeError(
        "DATABASE_NAME is not configured"
    )


client = AsyncIOMotorClient(
    settings.MONGODB_URL
)

database = client[settings.DATABASE_NAME]