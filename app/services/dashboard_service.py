# D:\Github\kitchen\backend\app\services\dashboard_service.py
from datetime import datetime, timezone

from app.core.database import database
from app.core.enums import OrderStatus


class DashboardService:
    async def get_dashboard(self) -> dict:
        orders = database["orders"]

        total_orders = await orders.count_documents({})
        placed_orders = await orders.count_documents({"status": OrderStatus.PLACED.value})
        preparing_orders = await orders.count_documents({"status": OrderStatus.PREPARING.value})
        out_for_delivery_orders = await orders.count_documents({"status": OrderStatus.OUT_FOR_DELIVERY.value})
        delivered_orders = await orders.count_documents({"status": OrderStatus.DELIVERED.value})
        cancelled_orders = await orders.count_documents({"status": OrderStatus.CANCELLED.value})

        active_orders = placed_orders + preparing_orders + out_for_delivery_orders
        pending_orders = placed_orders + preparing_orders

        revenue_cursor = await orders.aggregate([
            {
                "$match": {
                    "status": {"$ne": OrderStatus.CANCELLED.value}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total": {"$sum": "$total_amount"}
                }
            }
        ])
        revenue_result = await revenue_cursor.to_list(length=1)

        total_revenue = revenue_result[0]["total"] if revenue_result else 0

        now = datetime.now(timezone.utc)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day.replace(hour=23, minute=59, second=59, microsecond=999999)

        today_orders = await orders.count_documents({
            "created_at": {
                "$gte": start_of_day,
                "$lte": end_of_day
            }
        })

        today_revenue_cursor = await orders.aggregate([
            {
                "$match": {
                    "created_at": {
                        "$gte": start_of_day,
                        "$lte": end_of_day
                    },
                    "status": {"$ne": OrderStatus.CANCELLED.value}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total": {"$sum": "$total_amount"}
                }
            }
        ])
        today_revenue_result = await today_revenue_cursor.to_list(length=1)

        today_revenue = today_revenue_result[0]["total"] if today_revenue_result else 0

        return {
            "total_orders": total_orders,
            "placed_orders": placed_orders,
            "preparing_orders": preparing_orders,
            "out_for_delivery_orders": out_for_delivery_orders,
            "delivered_orders": delivered_orders,
            "cancelled_orders": cancelled_orders,
            "active_orders": active_orders,
            "pending_orders": pending_orders,
            "total_revenue": total_revenue,
            "today_orders": today_orders,
            "today_revenue": today_revenue
        }


dashboard_service = DashboardService()