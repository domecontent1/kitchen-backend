# backend/app/routes/notifications.py
from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import get_current_user
from app.schemas.notification import NotificationResponse
from app.services.notification_service import notification_service


router = APIRouter(prefix="/notifications", tags=["Notifications"])


def notification_to_response(notification: dict) -> dict:
    return {
        "id": str(notification["_id"]),
        "order_id": str(notification["order_id"]) if notification.get("order_id") else None,
        "title": notification["title"],
        "message": notification["message"],
        "type": notification["type"],
        "read": notification["read"],
        "created_at": notification["created_at"].isoformat()
    }


@router.get("/", response_model=list[NotificationResponse])
async def get_notifications(current_user: dict = Depends(get_current_user)):
    notifications = await notification_service.get_user_notifications(
        user_id=str(current_user["_id"]))

    return [notification_to_response(notification) for notification in notifications]


@router.get("/unread-count")
async def get_unread_notification_count(
    current_user: dict = Depends(get_current_user)
):
    count = await notification_service.get_unread_count(
        user_id=str(current_user["_id"]))

    return {"count": count}


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user)):
    notification = await notification_service.mark_as_read(
        notification_id=notification_id,
        user_id=str(current_user["_id"]))

    if notification is None:
        raise HTTPException(status_code=404,
            detail="Notification not found")

    return notification_to_response(notification)


@router.patch("/read-all")
async def mark_all_notifications_as_read(
    current_user: dict = Depends(get_current_user)
):
    count = await notification_service.mark_all_as_read(
        user_id=str(current_user["_id"])
    )

    return {
        "message": "Notifications marked as read",
        "count": count
    }