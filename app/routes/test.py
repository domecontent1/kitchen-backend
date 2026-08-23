from fastapi import APIRouter

from app.core.database import database


router = APIRouter()


@router.get("/db-test")
async def database_test():
    result = await database.command("ping")

    return {
        "message": "MongoDB connection successful",
        "mongodb_response": result
    }

