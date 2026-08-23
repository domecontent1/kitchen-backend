import asyncio
import getpass

from app.core.database import database
from app.core.security import hash_password
from app.schemas.user import UserRole
from datetime import datetime, timezone

async def create_admin():

    name = input("Admin name: ").strip()
    phone = input("Admin phone: ").strip()

    password = getpass.getpass(
        "Admin password: "
    )

    confirm_password = getpass.getpass(
        "Confirm password: "
    )

    if password != confirm_password:
        print("Passwords do not match.")
        return

    existing_user = await database["users"].find_one(
        {"phone": phone}
    )

    if existing_user is not None:
        print("A user with this phone number already exists.")
        return

    password_hash = hash_password(password)
    now = datetime.now(timezone.utc)
    user_data = {
        "name": name,
        "phone": phone,
        "password_hash": password_hash,
        "role": UserRole.ADMIN.value,
        "active": True,
        "created_at": now,
        "updated_at": now
    }

    result = await database["users"].insert_one(
        user_data
    )

    print(
        f"Admin created successfully: {result.inserted_id}"
    )


if __name__ == "__main__":
    asyncio.run(create_admin())