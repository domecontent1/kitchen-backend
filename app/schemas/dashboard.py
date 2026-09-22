# backend/app/schemas/dashboard.py
from pydantic import BaseModel


class DashboardResponse(BaseModel):
    total_orders: int
    placed_orders: int
    preparing_orders: int
    out_for_delivery_orders: int
    delivered_orders: int
    cancelled_orders: int
    active_orders: int
    pending_orders: int
    total_revenue: float
    today_orders: int
    today_revenue: float