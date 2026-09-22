# backend/app/services/notification_service.py
from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId

from app.core.database import database


class NotificationService:
    async def create_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        notification_type: str,
        order_id: Optional[str] = None
    ):
        notification = {
            "user_id": ObjectId(user_id),
            "order_id": (
                ObjectId(order_id)
                if order_id and ObjectId.is_valid(order_id)
                else None
            ),
            "title": title,
            "message": message,
            "type": notification_type,
            "read": False,
            "created_at": datetime.now(timezone.utc)
        }

        result = await database["notifications"].insert_one(notification)

        return await database["notifications"].find_one(
            {"_id": result.inserted_id}
        )

    async def get_user_notifications(self, user_id: str):
        cursor = database["notifications"].find(
            {"user_id": ObjectId(user_id)}
        ).sort("created_at", -1)

        notifications = []

        async for notification in cursor:
            notifications.append(notification)

        return notifications

    async def mark_as_read(
        self,
        notification_id: str,
        user_id: str
    ):
        if not ObjectId.is_valid(notification_id):
            return None

        result = await database["notifications"].update_one(
            {
                "_id": ObjectId(notification_id),
                "user_id": ObjectId(user_id)
            },
            {"$set": {"read": True}}
        )

        if result.matched_count == 0:
            return None

        return await database["notifications"].find_one(
            {
                "_id": ObjectId(notification_id),
                "user_id": ObjectId(user_id)
            }
        )

    async def mark_all_as_read(self, user_id: str):
        result = await database["notifications"].update_many(
            {
                "user_id": ObjectId(user_id),
                "read": False
            },
            {"$set": {"read": True}}
        )

        return result.modified_count

    async def get_unread_count(self, user_id: str) -> int:
        return await database["notifications"].count_documents(
            {
                "user_id": ObjectId(user_id),
                "read": False
            }
        )


notification_service = NotificationService()