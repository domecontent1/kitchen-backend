# app/services/address_service.py
from datetime import datetime, timezone

from bson import ObjectId

from app.core.database import database


class AddressService:

    async def create_address(
        self,
        user_id: str,
        address_data: dict
    ):

        now = datetime.now(timezone.utc)

        address_data["user_id"] = ObjectId(user_id)
        address_data["active"] = True
        address_data["created_at"] = now
        address_data["updated_at"] = now

        result = await database["addresses"].insert_one(
            address_data
        )

        return await database["addresses"].find_one(
            {"_id": result.inserted_id}
        )

    async def get_user_addresses(
        self,
        user_id: str
    ):

        cursor = database["addresses"].find(
            {
                "user_id": ObjectId(user_id),
                "active": True
            }
        )

        addresses = []

        async for address in cursor:
            addresses.append(address)

        return addresses

    async def get_address(
        self,
        address_id: str,
        user_id: str
    ):

        if not ObjectId.is_valid(address_id):
            return None

        return await database["addresses"].find_one(
            {
                "_id": ObjectId(address_id),
                "user_id": ObjectId(user_id),
                "active": True
            }
        )

    async def update_address(
        self,
        address_id: str,
        user_id: str,
        address_data: dict
    ):

        if not ObjectId.is_valid(address_id):
            return None

        address_data["updated_at"] = (
            datetime.now(timezone.utc)
        )

        result = await database["addresses"].update_one(
            {
                "_id": ObjectId(address_id),
                "user_id": ObjectId(user_id),
                "active": True
            },
            {
                "$set": address_data
            }
        )

        if result.matched_count == 0:
            return None

        return await database["addresses"].find_one(
            {
                "_id": ObjectId(address_id),
                "user_id": ObjectId(user_id)
            }
        )

    async def deactivate_address(
        self,
        address_id: str,
        user_id: str
    ):

        if not ObjectId.is_valid(address_id):
            return 0

        result = await database["addresses"].update_one(
            {
                "_id": ObjectId(address_id),
                "user_id": ObjectId(user_id),
                "active": True
            },
            {
                "$set": {
                    "active": False,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )

        return result.matched_count


address_service = AddressService()