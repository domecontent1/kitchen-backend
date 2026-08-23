from app.core.database import database


async def create_indexes():

    await database["users"].create_index(
        "phone",
        unique=True
    )