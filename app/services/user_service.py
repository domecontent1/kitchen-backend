# D:\Github\kitchen\backend\app\services\user_service.py
import math
import re
from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId

from app.core.database import database
from app.core.security import hash_password
from app.schemas.user import UserRole


class UserService:
    async def get_user_by_phone(self, phone: str):
        return await database["users"].find_one({"phone": phone})

    async def get_user_by_id(self, user_id: str):
        if not ObjectId.is_valid(user_id):
            return None
        return await database["users"].find_one({"_id": ObjectId(user_id)})

    async def create_customer(self, name: str, phone: str, password: str):
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
        result = await database["users"].insert_one(user_data)
        return await database["users"].find_one({"_id": result.inserted_id})

    async def update_profile(self, user_id: str, name: str):
        if not ObjectId.is_valid(user_id):
            return None
        result = await database["users"].update_one(
            {"_id": ObjectId(user_id), "active": True},
            {"$set": {"name": name.strip(), "updated_at": datetime.now(timezone.utc)}}
        )
        if result.matched_count == 0:
            return None
        return await database["users"].find_one(
            {"_id": ObjectId(user_id), "active": True}
        )

    async def get_admin_customers(
        self,
        page: int,
        page_size: int,
        search: Optional[str],
        active: Optional[bool]
    ):
        skip = (page - 1) * page_size
        user_query = {"role": UserRole.CUSTOMER.value}

        if active is not None:
            user_query["active"] = active

        if search:
            escaped_search = re.escape(search.strip())
            user_query["$or"] = [
                {"name": {"$regex": escaped_search, "$options": "i"}},
                {"phone": {"$regex": escaped_search, "$options": "i"}}
            ]

        users_collection = database["users"]
        total = await users_collection.count_documents(user_query)

        users = []
        cursor = (
            users_collection.find(user_query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(page_size)
        )

        async for user in cursor:
            users.append(user)

        customer_ids = [user["_id"] for user in users]
        order_stats = {}

        if customer_ids:
            pipeline = [
                {"$match": {"customer_id": {"$in": customer_ids}}},
                {
                    "$group": {
                        "_id": "$customer_id",
                        "order_count": {"$sum": 1},
                        "total_spent": {"$sum": "$total_amount"}
                    }
                }
            ]

            stats_cursor = await database["orders"].aggregate(pipeline)

            async for stats in stats_cursor:
                order_stats[stats["_id"]] = stats

        items = []

        for user in users:
            stats = order_stats.get(user["_id"], {})
            items.append({
                "id": str(user["_id"]),
                "name": user["name"],
                "phone": user["phone"],
                "active": user["active"],
                "order_count": stats.get("order_count", 0),
                "total_spent": stats.get("total_spent", 0)
            })

        return {
            "items": items,
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": math.ceil(total / page_size) if total else 0
        }

    async def get_admin_customer_details(self, customer_id: str):
        if not ObjectId.is_valid(customer_id):
            return None

        customer = await database["users"].find_one({
            "_id": ObjectId(customer_id),
            "role": UserRole.CUSTOMER.value
        })

        if customer is None:
            return None

        orders = []
        total_spent = 0

        cursor = (
            database["orders"]
            .find({"customer_id": ObjectId(customer_id)})
            .sort("created_at", -1)
        )

        async for order in cursor:
            total_amount = order.get("total_amount", 0)
            total_spent += total_amount

            orders.append({
                "id": str(order["_id"]),
                "status": order["status"],
                "total_amount": total_amount,
                "delivery_date": (
                    order["delivery_date"].isoformat()
                    if hasattr(order["delivery_date"], "isoformat")
                    else str(order["delivery_date"])
                ),
                "delivery_slot": order["delivery_slot"],
                "created_at": (
                    order["created_at"].isoformat()
                    if hasattr(order["created_at"], "isoformat")
                    else str(order["created_at"])
                )
            })

        return {
            "id": str(customer["_id"]),
            "name": customer["name"],
            "phone": customer["phone"],
            "active": customer["active"],
            "order_count": len(orders),
            "total_spent": total_spent,
            "orders": orders
        }


user_service = UserService()