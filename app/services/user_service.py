# app/services/user_service.py

from datetime import datetime, timezone

from bson import ObjectId

from app.core.database import database
from app.core.security import hash_password
from app.schemas.user import UserRole


class UserService:

    async def get_user_by_phone(self, phone: str):

        return await database["users"].find_one(
            {"phone": phone}
        )

    async def get_user_by_id(self, user_id: str):

        if not ObjectId.is_valid(user_id):
            return None

        return await database["users"].find_one(
            {"_id": ObjectId(user_id)}
        )

    async def create_customer(
        self,
        name: str,
        phone: str,
        password: str
    ):

        password_hash = hash_password(password)

        now = datetime.now(timezone.utc)

        user_data = {
            "name": name,
            "phone": phone,
            "password_hash": password_hash,
            "role": UserRole.CUSTOMER.value,
            "active": True,
            "created_at": now,
            "updated_at": now
        }

        result = await database["users"].insert_one(
            user_data
        )

        return await database["users"].find_one(
            {"_id": result.inserted_id}
        )


user_service = UserService()