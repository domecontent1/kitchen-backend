# backend/app/services/notification_service.py
import asyncio
import hashlib
from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from fastapi import HTTPException
from pymongo.errors import (
    AutoReconnect,
    ConnectionFailure,
    DuplicateKeyError,
    PyMongoError,
    WTimeoutError
)

from app.core.database import database

MAX_CREATE_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 0.05
TRANSIENT_WRITE_ERRORS = (AutoReconnect, ConnectionFailure, WTimeoutError)


class NotificationService:
    @staticmethod
    def _event_filter(
        user_id: ObjectId,
        order_id: ObjectId,
        title: str,
        notification_type: str
    ) -> dict:
        return {
            "user_id": user_id,
            "order_id": order_id,
            "title": title,
            "type": notification_type
        }

    async def find_order_notification(
        self,
        user_id: str,
        order_id: str,
        title: str,
        notification_type: str
    ):
        if not ObjectId.is_valid(user_id) or not ObjectId.is_valid(order_id):
            return None

        return await database["notifications"].find_one(
            self._event_filter(
                ObjectId(user_id),
                ObjectId(order_id),
                title,
                notification_type
            )
        )

    @staticmethod
    def _stable_order_event_id(
        user_id: ObjectId,
        order_id: ObjectId,
        title: str,
        notification_type: str
    ) -> ObjectId:
        identity = "\x1f".join((
            str(user_id),
            str(order_id),
            notification_type,
            title
        ))
        return ObjectId(hashlib.sha256(identity.encode("utf-8")).digest()[:12])

    @staticmethod
    def _same_event(notification: Optional[dict], event_filter: dict) -> bool:
        return bool(notification) and all(
            notification.get(key) == value
            for key, value in event_filter.items()
        )

    async def _existing_order_event(
        self,
        collection,
        notification_id: ObjectId,
        event_filter: dict
    ):
        notification = await collection.find_one({"_id": notification_id})
        if self._same_event(notification, event_filter):
            return notification
        return await collection.find_one(event_filter)

    async def create_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        notification_type: str,
        order_id: Optional[str] = None
    ):
        user_object_id = ObjectId(user_id)
        order_object_id = (
            ObjectId(order_id)
            if order_id and ObjectId.is_valid(order_id)
            else None
        )
        event_filter = (
            self._event_filter(
                user_object_id,
                order_object_id,
                title,
                notification_type
            )
            if order_object_id is not None
            else None
        )
        notification_id = (
            self._stable_order_event_id(
                user_object_id,
                order_object_id,
                title,
                notification_type
            )
            if order_object_id is not None
            else ObjectId()
        )
        notification = {
            "_id": notification_id,
            "user_id": user_object_id,
            "order_id": order_object_id,
            "title": title,
            "message": message,
            "type": notification_type,
            "read": False,
            "created_at": datetime.now(timezone.utc)
        }

        collection = database["notifications"]

        for attempt in range(MAX_CREATE_ATTEMPTS):
            try:
                if event_filter is not None:
                    existing = await collection.find_one(event_filter)
                    if existing is not None:
                        return existing

                await collection.insert_one(notification)
                return notification
            except DuplicateKeyError as error:
                existing = None
                if event_filter is not None:
                    existing = await self._existing_order_event(
                        collection,
                        notification_id,
                        event_filter
                    )
                if existing is not None:
                    return existing
                raise HTTPException(
                    status_code=503,
                    detail="Could not save the order notification. Please retry the request."
                ) from error
            except PyMongoError as error:
                is_transient = isinstance(error, TRANSIENT_WRITE_ERRORS)
                if hasattr(error, "has_error_label"):
                    is_transient = is_transient or error.has_error_label(
                        "RetryableWriteError"
                    )

                if not is_transient:
                    raise HTTPException(
                        status_code=503,
                        detail="Could not save the order notification. Please retry the request."
                    ) from error

                if event_filter is not None:
                    try:
                        existing = await self._existing_order_event(
                            collection,
                            notification_id,
                            event_filter
                        )
                    except PyMongoError:
                        existing = None
                    if existing is not None:
                        return existing

                if attempt + 1 == MAX_CREATE_ATTEMPTS:
                    raise HTTPException(
                        status_code=503,
                        detail="Could not save the order notification after several attempts. Please retry the request."
                    ) from error

                await asyncio.sleep(RETRY_DELAY_SECONDS * (2 ** attempt))

        raise HTTPException(
            status_code=503,
            detail="Could not save the order notification. Please retry the request."
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
