# backend/app/core/settings.py
import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    MONGODB_URL: str = os.getenv("MONGODB_URL", "")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

settings = Settings()


if not settings.MONGODB_URL:
    raise RuntimeError("MONGODB_URL is not configured")

if not settings.DATABASE_NAME:
    raise RuntimeError("DATABASE_NAME is not configured")

if not settings.JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is not configured")

if settings.ACCESS_TOKEN_EXPIRE_MINUTES <= 0:
    raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES must be greater than 0")