# app/services/order_service.py

from datetime import date, datetime, time, timezone

from bson import ObjectId
from fastapi import HTTPException

from app.core.database import database
from app.services.delivery_service import delivery_service


class OrderService:

    async def create_order(
        self,
        customer_id: str,
        order_data: dict
    ):

        if not ObjectId.is_valid(customer_id):
            raise HTTPException(
                status_code=400,
                detail="Invalid customer ID"
            )

        customer_object_id = ObjectId(customer_id)
        customer = await database["users"].find_one(
            {"_id": customer_object_id}
        )

        if customer is None:
            raise HTTPException(
                status_code=404,
                detail="Customer not found"
            )

        address_id = order_data["address_id"]

        if not ObjectId.is_valid(address_id):
            raise HTTPException(
                status_code=400,
                detail="Invalid address ID"
            )

        address = await database["addresses"].find_one(
            {
                "_id": ObjectId(address_id),
                "user_id": customer_object_id,
                "active": True
            }
        )

        if address is None:
            raise HTTPException(
                status_code=404,
                detail="Address not found"
            )

        delivery_date = order_data["delivery_date"]

        delivery_service.validate_delivery_date(
            delivery_date
        )

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
            raise HTTPException(
                status_code=400,
                detail="Order must contain at least one dish"
            )

        dish_ids = [
            item["dish_id"]
            for item in requested_items
        ]

        if len(dish_ids) != len(set(dish_ids)):
            raise HTTPException(
                status_code=400,
                detail="Duplicate dishes are not allowed in an order"
            )

        order_items = []
        total_amount = 0.0

        for item in requested_items:

            dish_id = item["dish_id"]
            quantity = item["quantity"]

            if not ObjectId.is_valid(dish_id):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid dish ID"
                )

            dish = await database["dishes"].find_one(
                {
                    "_id": ObjectId(dish_id),
                    "active": True
                }
            )

            if dish is None:
                raise HTTPException(
                    status_code=404,
                    detail="Dish not found or inactive"
                )

            price = float(dish["price"])
            subtotal = price * quantity

            order_items.append(
                {
                    "dish_id": str(dish["_id"]),
                    "name": dish["name"],
                    "price": price,
                    "quantity": quantity,
                    "subtotal": subtotal
                }
            )

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
            "customer": {
                "name": customer["name"],
                "phone": customer["phone"]
            },
            "items": order_items,
            "delivery_date": delivery_date,
            "delivery_slot": delivery_slot,
            "delivery_address": delivery_address,
            "total_amount": total_amount,
            "status": "PLACED",
            "notes": order_data.get("notes"),
            "created_at": now,
            "updated_at": now
        }

        if (
            isinstance(order_document.get("delivery_date"), date)
            and not isinstance(
                order_document.get("delivery_date"),
                datetime
            )
        ):
            order_document["delivery_date"] = datetime.combine(
                order_document["delivery_date"],
                time.min
            )

        result = await database["orders"].insert_one(
            order_document
        )

        return await database["orders"].find_one(
            {
                "_id": result.inserted_id
            }
        )

    async def get_customer_orders(
            self,
            customer_id: str
    ):
        if not ObjectId.is_valid(customer_id):
            return []

        cursor = database["orders"].find(
            {
                "customer_id": ObjectId(customer_id)
            }
        ).sort(
            "created_at",
            -1
        )

        orders = []

        async for order in cursor:
            orders.append(
                await self.attach_customer(order)
            )

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

        order = await database["orders"].find_one(
            {
                "_id": ObjectId(order_id),
                "customer_id": ObjectId(customer_id)
            }
        )

        if order:
            await self.attach_customer(order)

        return order

    async def get_all_orders(self):
        cursor = database["orders"].find({}).sort(
            "created_at",
            -1
        )

        orders = []

        async for order in cursor:
            orders.append(
                await self.attach_customer(order)
            )

        return orders

    async def update_order_status(
        self,
        order_id: str,
        new_status: str
    ):

        if not ObjectId.is_valid(order_id):
            return None

        order = await database["orders"].find_one(
            {
                "_id": ObjectId(order_id)
            }
        )

        if order is None:
            return None

        current_status = order["status"]

        allowed_transitions = {
            "PLACED": [
                "PREPARING",
                "CANCELLED"
            ],
            "PREPARING": [
                "OUT_FOR_DELIVERY",
                "CANCELLED"
            ],
            "OUT_FOR_DELIVERY": [
                "DELIVERED"
            ],
            "DELIVERED": [],
            "CANCELLED": []
        }

        if new_status not in allowed_transitions.get(
            current_status,
            []
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Cannot change order status "
                    f"from {current_status} to {new_status}"
                )
            )

        result = await database["orders"].update_one(
            {
                "_id": ObjectId(order_id)
            },
            {
                "$set": {
                    "status": new_status,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )

        if result.matched_count == 0:
            return None

        updated_order = await database["orders"].find_one(
            {
                "_id": ObjectId(order_id)
            }
        )

        if updated_order:
            await self.attach_customer(updated_order)

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

        order = await database["orders"].find_one(
            {
                "_id": ObjectId(order_id),
                "customer_id": ObjectId(customer_id)
            }
        )

        if order is None:
            return None

        if order["status"] != "PLACED":
            raise HTTPException(
                status_code=400,
                detail="Only placed orders can be cancelled"
            )

        result = await database["orders"].update_one(
            {
                "_id": ObjectId(order_id),
                "customer_id": ObjectId(customer_id)
            },
            {
                "$set": {
                    "status": "CANCELLED",
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )

        if result.matched_count == 0:
            return None

        cancelled_order = await database["orders"].find_one(
            {
                "_id": ObjectId(order_id)
            }
        )

        if cancelled_order:
            await self.attach_customer(cancelled_order)

        return cancelled_order

    async def attach_customer(self, order: dict):
        customer = await database["users"].find_one(
            {"_id": order["customer_id"]},
            {"name": 1, "phone": 1}
        )

        order["customer"] = {
            "name": customer["name"] if customer else "Unknown Customer",
            "phone": customer["phone"] if customer else "Unknown"
        }

        return order


order_service = OrderService()