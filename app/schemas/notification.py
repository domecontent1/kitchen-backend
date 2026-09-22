# backend/app/schemas/notification.py
from typing import Optional

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: str
    order_id: Optional[str]
    title: str
    message: str
    type: str
    read: bool
    created_at: str