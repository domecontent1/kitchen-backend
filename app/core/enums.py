# backend/app/core/enums.py
from enum import StrEnum


class OrderStatus(StrEnum):
    PLACED = "PLACED"
    PREPARING = "PREPARING"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"