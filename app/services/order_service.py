# backend/app/services/order_service.py
import re
from datetime import date, datetime, time, timezone
from typing import Optional

from bson import ObjectId
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError

from app.core.database import database
from app.core.enums import OrderStatus
from app.services.delivery_service import delivery_service
from app.services.notification_service import notification_service


class OrderService:
    async def create_order(
        self,
        customer_id: str,
        order_data: dict,
        idempotency_key: str
    ):
        if not ObjectId.is_valid(customer_id):
            raise HTTPException(status_code=400, detail="Invalid customer ID")

        customer_object_id = ObjectId(customer_id)
        existing_order = await database["orders"].find_one({
            "customer_id": customer_object_id,
            "idempotency_key": idempotency_key
        })

        if existing_order is not None:
            return existing_order

        customer = await database["users"].find_one({"_id": customer_object_id})

        if customer is None:
            raise HTTPException(status_code=404, detail="Customer not found")

        address_id = order_data["address_id"]

        if not ObjectId.is_valid(address_id):
            raise HTTPException(status_code=400, detail="Invalid address ID")

        address = await database["addresses"].find_one({
            "_id": ObjectId(address_id),
            "user_id": customer_object_id,
            "active": True
        })

        if address is None:
            raise HTTPException(status_code=404, detail="Address not found")

        delivery_date = order_data["delivery_date"]

        delivery_service.validate_delivery_date(delivery_date)
        delivery_service.validate_delivery_slot(
            delivery_date=delivery_date,
            start_time=order_data["delivery_slot"]["start"],
            end_time=order_data["delivery_slot"]["end"]
        )

        delivery_slot = {
            "start": order_data["delivery_slot"]["start"].strftime("%H:%M"),
            "end": order_data["delivery_slot"]["end"].strftime("%H:%M")
        }

        requested_items = order_data["items"]

        if not requested_items:
            raise HTTPException(status_code=400,
                detail="Order must contain at least one dish")

        dish_ids = [item["dish_id"] for item in requested_items]

        if len(dish_ids) != len(set(dish_ids)):
            raise HTTPException(status_code=400,
                detail="Duplicate dishes are not allowed in an order")

        order_items = []
        total_amount = 0.0

        for item in requested_items:
            dish_id = item["dish_id"]
            quantity = item["quantity"]

            if not ObjectId.is_valid(dish_id):
                raise HTTPException(status_code=400,
                    detail="Invalid dish ID")

            dish = await database["dishes"].find_one({
                "_id": ObjectId(dish_id),
                "active": True
            })

            if dish is None:
                raise HTTPException(status_code=404,
                    detail="Dish not found or inactive")

            price = float(dish["price"])
            subtotal = price * quantity

            order_items.append({
                "dish_id": str(dish["_id"]),
                "name": dish["name"],
                "price": price,
                "quantity": quantity,
                "subtotal": subtotal
            })

            total_amount += subtotal

        delivery_address = {
            "label": address["label"],
            "address_line": address["address_line"],
            "landmark": address.get("landmark"),
            "town": address["town"],
            "pincode": address["pincode"]
        }

        now = datetime.now(timezone.utc)

        order_document = {
            "customer_id": customer_object_id,
            "idempotency_key": idempotency_key,
            "customer": {
                "name": customer["name"],
                "phone": customer["phone"]
            },
            "items": order_items,
            "delivery_date": delivery_date,
            "delivery_slot": delivery_slot,
            "delivery_address": delivery_address,
            "total_amount": total_amount,
            "status": OrderStatus.PLACED.value,
            "notes": order_data.get("notes"),
            "created_at": now,
            "updated_at": now
        }

        if (
            isinstance(order_document.get("delivery_date"), date)
            and not isinstance(order_document.get("delivery_date"), datetime)
        ):
            order_document["delivery_date"] = datetime.combine(
                order_document["delivery_date"],
                time.min
            )

        try:
            result = await database["orders"].insert_one(order_document)
        except DuplicateKeyError:
            existing_order = await database["orders"].find_one({
                "customer_id": customer_object_id,
                "idempotency_key": idempotency_key
            })

            if existing_order is not None:
                return existing_order

            raise

        return await database["orders"].find_one({
            "_id": result.inserted_id
        })

    async def get_customer_orders(self, customer_id: str):
        if not ObjectId.is_valid(customer_id):
            return []

        cursor = database["orders"].find({
            "customer_id": ObjectId(customer_id)
        }).sort("created_at", -1)

        orders = []

        async for order in cursor:
            orders.append(await self.ensure_customer_snapshot(order))

        return orders

    async def get_order_by_id(
        self,
        order_id: str,
        customer_id: str
    ):
        if not ObjectId.is_valid(order_id):
            return None

        if not ObjectId.is_valid(customer_id):
            return None

        order = await database["orders"].find_one({
            "_id": ObjectId(order_id),
            "customer_id": ObjectId(customer_id)
        })

        if order:
            await self.ensure_customer_snapshot(order)

        return order

    async def get_admin_orders(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[OrderStatus] = None,
        search: Optional[str] = None
    ):
        if page < 1:
            raise HTTPException(status_code=400,
                detail="Page must be greater than or equal to 1")

        if page_size < 1 or page_size > 100:
            raise HTTPException(status_code=400,
                detail="Page size must be between 1 and 100")

        query = {}

        if status:
            query["status"] = status.value

        if search:
            search = search.strip()

            if search:
                search_pattern = {
                    "$regex": re.escape(search),
                    "$options": "i"
                }

                matching_customers = await database["users"].find(
                    {
                        "$or": [
                            {"name": search_pattern},
                            {"phone": search_pattern}
                        ]
                    },
                    {"_id": 1}
                ).to_list(length=None)

                customer_ids = [
                    customer["_id"]
                    for customer in matching_customers
                ]

                query["$or"] = [
                    {"customer.name": search_pattern},
                    {"customer.phone": search_pattern}
                ]

                if customer_ids:
                    query["$or"].append({
                        "customer_id": {"$in": customer_ids}
                    })

                if ObjectId.is_valid(search):
                    query["$or"].append({
                        "_id": ObjectId(search)
                    })

        total = await database["orders"].count_documents(query)
        skip = (page - 1) * page_size

        cursor = (
            database["orders"]
            .find(query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(page_size)
        )

        orders = []

        async for order in cursor:
            await self.ensure_customer_snapshot(order)
            orders.append(order)

        total_pages = (
            (total + page_size - 1) // page_size
            if total > 0
            else 0
        )

        return {
            "items": orders,
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages
        }

    async def update_order_status(
        self,
        order_id: str,
        new_status: OrderStatus
    ):
        if not ObjectId.is_valid(order_id):
            return None

        order = await database["orders"].find_one({
            "_id": ObjectId(order_id)
        })

        if order is None:
            return None

        current_status = OrderStatus(order["status"])

        allowed_transitions = {
            OrderStatus.PLACED: [
                OrderStatus.PREPARING,
                OrderStatus.CANCELLED
            ],
            OrderStatus.PREPARING: [
                OrderStatus.OUT_FOR_DELIVERY,
                OrderStatus.CANCELLED
            ],
            OrderStatus.OUT_FOR_DELIVERY: [
                OrderStatus.DELIVERED
            ],
            OrderStatus.DELIVERED: [],
            OrderStatus.CANCELLED: []
        }

        if new_status not in allowed_transitions.get(current_status, []):
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Cannot change order status "
                    f"from {current_status} to {new_status}"
                )
            )

        result = await database["orders"].update_one(
            {"_id": ObjectId(order_id)},
            {
                "$set": {
                    "status": new_status.value,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )

        if result.matched_count == 0:
            return None

        updated_order = await database["orders"].find_one({
            "_id": ObjectId(order_id)
        })

        if updated_order:
            await self.ensure_customer_snapshot(updated_order)

            notification_messages = {
                OrderStatus.PREPARING: "Your order is now being prepared.",
                OrderStatus.OUT_FOR_DELIVERY: "Your order is out for delivery.",
                OrderStatus.DELIVERED: "Your order has been delivered.",
                OrderStatus.CANCELLED: "Your order has been cancelled."
            }

            message = notification_messages.get(new_status)

            if message:
                await notification_service.create_notification(
                    user_id=str(updated_order["customer_id"]),
                    order_id=str(updated_order["_id"]),
                    title=f"Order {new_status.value.replace('_', ' ').title()}",
                    message=message,
                    notification_type="ORDER_STATUS"
                )

        return updated_order

    async def cancel_customer_order(
        self,
        order_id: str,
        customer_id: str
    ):
        if not ObjectId.is_valid(order_id):
            return None

        if not ObjectId.is_valid(customer_id):
            return None

        order = await database["orders"].find_one({
            "_id": ObjectId(order_id),
            "customer_id": ObjectId(customer_id)
        })

        if order is None:
            return None

        if order["status"] != OrderStatus.PLACED.value:
            raise HTTPException(status_code=400,
                detail="Only placed orders can be cancelled")

        result = await database["orders"].update_one(
            {
                "_id": ObjectId(order_id),
                "customer_id": ObjectId(customer_id)
            },
            {
                "$set": {
                    "status": OrderStatus.CANCELLED.value,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )

        if result.matched_count == 0:
            return None

        cancelled_order = await database["orders"].find_one({
            "_id": ObjectId(order_id)
        })

        if cancelled_order:
            await self.ensure_customer_snapshot(cancelled_order)

        return cancelled_order

    async def ensure_customer_snapshot(self, order: dict):
        customer = order.get("customer")

        if (
            isinstance(customer, dict)
            and customer.get("name")
            and customer.get("phone")
        ):
            return order

        customer_id = order.get("customer_id")

        if (
            not customer_id
            or not ObjectId.is_valid(str(customer_id))
        ):
            return order

        customer = await database["users"].find_one(
            {"_id": ObjectId(str(customer_id))},
            {"name": 1, "phone": 1}
        )

        if customer:
            order["customer"] = {
                "name": customer["name"],
                "phone": customer["phone"]
            }

        return order

    async def get_admin_order_by_id(self, order_id: str):
        if not ObjectId.is_valid(order_id):
            return None

        order = await database["orders"].find_one({
            "_id": ObjectId(order_id)
        })

        if order:
            await self.ensure_customer_snapshot(order)

        return order

    async def get_admin_order_status_counts(self):
        collection = database["orders"]

        counts = {
            "ALL": await collection.count_documents({}),
            "PLACED": await collection.count_documents({
                "status": OrderStatus.PLACED.value
            }),
            "PREPARING": await collection.count_documents({
                "status": OrderStatus.PREPARING.value
            }),
            "OUT_FOR_DELIVERY": await collection.count_documents({
                "status": OrderStatus.OUT_FOR_DELIVERY.value
            }),
            "DELIVERED": await collection.count_documents({
                "status": OrderStatus.DELIVERED.value
            }),
            "CANCELLED": await collection.count_documents({
                "status": OrderStatus.CANCELLED.value
            })
        }

        return counts


order_service = OrderService()