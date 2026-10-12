# D:\Github\kitchen\backend\tests\test_orders.py
import asyncio
from datetime import date, datetime, time, timedelta, timezone
from uuid import uuid4

import pytest
from bson import ObjectId
from fastapi import HTTPException

from app.core.auth import require_admin
from app.core.database import database
from app.core.enums import OrderStatus
from app.main import app
from app.services.order_service import order_service
import app.services.order_service as order_service_module
from app.core.security import hash_password
from app.services.notification_service import notification_service


ADMIN_PHONE = "9999999999"
ADMIN_PASSWORD = "AdminTestPassword123"


async def get_admin_token(client):
    existing_admin = await database["users"].find_one({"phone": ADMIN_PHONE})

    if existing_admin is None:
        now = datetime.now(timezone.utc)
        await database["users"].insert_one({
            "name": "Test Admin",
            "phone": ADMIN_PHONE,
            "password_hash": hash_password(ADMIN_PASSWORD),
            "role": "ADMIN",
            "active": True,
            "created_at": now,
            "updated_at": now
        })

    response = await client.post("/auth/token", data={
        "username": ADMIN_PHONE,
        "password": ADMIN_PASSWORD
    })
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


async def prepare_customer_order(client):
    phone = f"98{uuid4().int % 100000000:08d}"
    customer = await register_customer(client, phone)
    token = await login_customer(client, phone)
    address_id = await create_address(client, token)
    dish_id = await create_test_dish()
    response = await create_order(client, token, address_id, dish_id)
    assert response.status_code == 200, response.text
    return customer["id"], token, response.json()


async def test_admin_orders_for_date_uses_selected_date(test_client, monkeypatch):
    selected_date = "2026-09-29"
    requested_dates = []

    async def fake_get_admin_orders_for_date(delivery_date):
        requested_dates.append(delivery_date.isoformat())
        return {
            "items": [],
            "total_orders": 0,
            "placed_orders": 0,
            "preparing_orders": 0,
            "out_for_delivery_orders": 0,
            "delivered_orders": 0,
            "cancelled_orders": 0,
            "total_revenue": 0
        }

    monkeypatch.setattr(
        order_service,
        "get_admin_orders_for_date",
        fake_get_admin_orders_for_date
    )
    app.dependency_overrides[require_admin] = lambda: {
        "_id": "test-admin",
        "role": "ADMIN",
        "active": True
    }

    try:
        response = await test_client.get(
            "/orders/admin/today",
            params={"date": selected_date}
        )
    finally:
        app.dependency_overrides.pop(require_admin, None)

    assert response.status_code == 200, response.text
    assert requested_dates == [selected_date]
    assert response.json()["items"] == []


async def test_admin_orders_for_date_requires_date(test_client, monkeypatch):
    async def unexpected_service_call(_delivery_date):
        raise AssertionError("Service should not be called without a date")

    monkeypatch.setattr(
        order_service,
        "get_admin_orders_for_date",
        unexpected_service_call
    )
    app.dependency_overrides[require_admin] = lambda: {
        "_id": "test-admin",
        "role": "ADMIN",
        "active": True
    }

    try:
        response = await test_client.get("/orders/admin/today")
    finally:
        app.dependency_overrides.pop(require_admin, None)

    assert response.status_code == 422


async def test_admin_order_list_filters_by_delivery_date(test_client):
    _, _, matching_order = await prepare_customer_order(test_client)
    _, _, other_order = await prepare_customer_order(test_client)
    selected_date = date(2030, 4, 12)

    await database["orders"].update_one(
        {"_id": ObjectId(matching_order["id"])},
        {"$set": {"delivery_date": datetime.combine(selected_date, time.min)}}
    )
    await database["orders"].update_one(
        {"_id": ObjectId(other_order["id"])},
        {"$set": {
            "delivery_date": datetime.combine(
                selected_date + timedelta(days=1),
                time.min
            )
        }}
    )
    admin_token = await get_admin_token(test_client)

    response = await test_client.get(
        "/orders/admin",
        headers={"Authorization": f"Bearer {admin_token}"},
        params={"delivery_date": selected_date.isoformat()}
    )

    assert response.status_code == 200, response.text
    assert response.json()["total"] == 1
    assert [item["id"] for item in response.json()["items"]] == [
        matching_order["id"]
    ]


async def test_admin_order_list_combines_date_status_and_search_filters(
    test_client
):
    _, _, matching_order = await prepare_customer_order(test_client)
    _, _, wrong_status_order = await prepare_customer_order(test_client)
    _, _, wrong_date_order = await prepare_customer_order(test_client)
    selected_date = date(2030, 4, 12)

    for order, delivery_date, status in [
        (matching_order, selected_date, "PREPARING"),
        (wrong_status_order, selected_date, "CANCELLED"),
        (wrong_date_order, selected_date + timedelta(days=1), "PREPARING")
    ]:
        await database["orders"].update_one(
            {"_id": ObjectId(order["id"])},
            {"$set": {
                "delivery_date": datetime.combine(delivery_date, time.min),
                "status": status
            }}
        )

    admin_token = await get_admin_token(test_client)
    response = await test_client.get(
        "/orders/admin",
        headers={"Authorization": f"Bearer {admin_token}"},
        params={
            "delivery_date": selected_date.isoformat(),
            "status": "PREPARING",
            "search": "Test Customer"
        }
    )

    assert response.status_code == 200, response.text
    assert response.json()["total"] == 1
    assert [item["id"] for item in response.json()["items"]] == [
        matching_order["id"]
    ]


async def register_customer(client, phone):
    response = await client.post(
        "/auth/register",
        json={
            "name": "Test Customer",
            "phone": phone,
            "password": "CustomerPassword123"
        }
    )
    assert response.status_code == 200, response.text
    return response.json()


async def login_customer(client, phone):
    response = await client.post(
        "/auth/login",
        json={
            "phone": phone,
            "password": "CustomerPassword123"
        }
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


async def create_address(client, token):
    response = await client.post(
        "/addresses/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "label": "Home",
            "address_line": "123 Test Street",
            "landmark": "Near Test Market",
            "town": "Test Town",
            "pincode": "400001"
        }
    )
    assert response.status_code == 200, response.text
    return response.json()["id"]


async def create_test_dish():
    result = await database["dishes"].insert_one({
        "name": "Test Thali",
        "description": "Test dish",
        "category": "Lunch",
        "price": 150,
        "active": True,
        "image_url": None,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    })
    return str(result.inserted_id)


# D:\Github\kitchen\backend\tests\test_orders.py
async def create_order(client, token, address_id, dish_id, idempotency_key=None):
    delivery_date = (
        datetime.now(timezone.utc).date() + timedelta(days=1)
    ).isoformat()
    response = await client.post(
        "/orders/",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Idempotency-Key": idempotency_key or uuid4().hex
        },
        json={
            "address_id": address_id,
            "delivery_date": delivery_date,
            "delivery_slot": {
                "start": "11:00",
                "end": "12:00"
            },
            "items": [
                {
                    "dish_id": dish_id,
                    "quantity": 2
                }
            ],
            "notes": "Test order"
        }
    )
    return response
async def test_create_order_requires_authentication(test_client):
    response = await test_client.post(
        "/orders/",
        json={}
    )

    assert response.status_code in (401, 403)


async def test_customer_can_create_order(test_client):
    phone = f"98{uuid4().int % 100000000:08d}"

    await register_customer(test_client, phone)
    token = await login_customer(test_client, phone)
    address_id = await create_address(test_client, token)
    dish_id = await create_test_dish()

    response = await create_order(
        test_client,
        token,
        address_id,
        dish_id
    )

    assert response.status_code == 200, response.text

    order = response.json()

    assert order["status"] == "PLACED"
    assert order["total_amount"] == 300
    assert order["items"][0]["price"] == 150
    assert order["items"][0]["quantity"] == 2
    assert order["items"][0]["subtotal"] == 300
    placed_notification = await database["notifications"].find_one({
        "order_id": ObjectId(order["id"]),
        "title": "Order Placed"
    })
    assert placed_notification is not None
    assert placed_notification["read"] is False


async def test_customer_repeated_idempotency_key_returns_existing_order(
    test_client
):
    phone = f"98{uuid4().int % 100000000:08d}"
    customer = await register_customer(test_client, phone)
    token = await login_customer(test_client, phone)
    address_id = await create_address(test_client, token)
    dish_id = await create_test_dish()
    idempotency_key = uuid4().hex

    first_response = await create_order(
        test_client,
        token,
        address_id,
        dish_id,
        idempotency_key
    )
    second_response = await create_order(
        test_client,
        token,
        address_id,
        dish_id,
        idempotency_key
    )

    assert first_response.status_code == 200, first_response.text
    assert second_response.status_code == 200, second_response.text
    assert second_response.json()["id"] == first_response.json()["id"]
    matching_orders = await database["orders"].count_documents({
        "customer_id": ObjectId(customer["id"]),
        "idempotency_key": idempotency_key
    })
    assert matching_orders == 1


async def test_order_placement_retry_recovers_missing_notification(
    test_client,
    monkeypatch
):
    phone = f"98{uuid4().int % 100000000:08d}"
    customer = await register_customer(test_client, phone)
    token = await login_customer(test_client, phone)
    address_id = await create_address(test_client, token)
    dish_id = await create_test_dish()
    idempotency_key = uuid4().hex
    create_notification = notification_service.create_notification
    attempts = 0

    async def fail_first_notification(**kwargs):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise HTTPException(status_code=503, detail="Temporary notification failure")
        return await create_notification(**kwargs)

    monkeypatch.setattr(
        notification_service,
        "create_notification",
        fail_first_notification
    )

    failed_response = await create_order(
        test_client,
        token,
        address_id,
        dish_id,
        idempotency_key
    )
    retry_response = await create_order(
        test_client,
        token,
        address_id,
        dish_id,
        idempotency_key
    )

    assert failed_response.status_code == 503
    assert retry_response.status_code == 200, retry_response.text
    stored_order = await database["orders"].find_one({
        "customer_id": ObjectId(customer["id"]),
        "idempotency_key": idempotency_key
    })
    assert retry_response.json()["id"] == str(stored_order["_id"])
    assert await database["orders"].count_documents({
        "customer_id": ObjectId(customer["id"]),
        "idempotency_key": idempotency_key
    }) == 1
    assert await database["notifications"].count_documents({
        "user_id": ObjectId(customer["id"]),
        "order_id": ObjectId(retry_response.json()["id"]),
        "title": "Order Placed"
    }) == 1


async def test_customer_cancellation_retry_recovers_missing_notification(
    test_client,
    monkeypatch
):
    customer_id, token, order = await prepare_customer_order(test_client)
    create_notification = notification_service.create_notification
    attempts = 0

    async def fail_first_cancellation(**kwargs):
        nonlocal attempts
        if kwargs["title"] == "Order Cancelled":
            attempts += 1
            if attempts == 1:
                raise HTTPException(status_code=503, detail="Temporary notification failure")
        return await create_notification(**kwargs)

    monkeypatch.setattr(
        notification_service,
        "create_notification",
        fail_first_cancellation
    )

    failed_response = await test_client.patch(
        f"/orders/{order['id']}/cancel",
        headers={"Authorization": f"Bearer {token}"}
    )
    retry_response = await test_client.patch(
        f"/orders/{order['id']}/cancel",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert failed_response.status_code == 503
    assert retry_response.status_code == 200, retry_response.text
    assert retry_response.json()["status"] == "CANCELLED"
    assert await database["orders"].count_documents({
        "_id": ObjectId(order["id"]),
        "status": "CANCELLED"
    }) == 1
    assert await database["notifications"].count_documents({
        "user_id": ObjectId(customer_id),
        "order_id": ObjectId(order["id"]),
        "title": "Order Cancelled"
    }) == 1


async def test_admin_status_retry_recovers_missing_notification(
    test_client,
    monkeypatch
):
    _, _, order = await prepare_customer_order(test_client)
    admin_token = await get_admin_token(test_client)
    create_notification = notification_service.create_notification
    attempts = 0

    async def fail_first_preparing_notification(**kwargs):
        nonlocal attempts
        if kwargs["title"] == "Order Preparing":
            attempts += 1
            if attempts == 1:
                raise HTTPException(status_code=503, detail="Temporary notification failure")
        return await create_notification(**kwargs)

    monkeypatch.setattr(
        notification_service,
        "create_notification",
        fail_first_preparing_notification
    )

    failed_response = await test_client.patch(
        f"/orders/admin/{order['id']}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "PREPARING"}
    )
    retry_response = await test_client.patch(
        f"/orders/admin/{order['id']}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "PREPARING"}
    )

    assert failed_response.status_code == 503
    assert retry_response.status_code == 200, retry_response.text
    assert retry_response.json()["status"] == "PREPARING"
    assert await database["notifications"].count_documents({
        "order_id": ObjectId(order["id"]),
        "title": "Order Preparing"
    }) == 1


async def test_customer_can_retrieve_own_orders(test_client):
    phone = f"98{uuid4().int % 100000000:08d}"

    await register_customer(test_client, phone)
    token = await login_customer(test_client, phone)
    address_id = await create_address(test_client, token)
    dish_id = await create_test_dish()

    create_response = await create_order(
        test_client,
        token,
        address_id,
        dish_id
    )

    assert create_response.status_code == 200

    order_id = create_response.json()["id"]

    response = await test_client.get(
        "/orders/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200, response.text

    orders = response.json()

    assert any(order["id"] == order_id for order in orders)


async def test_customer_can_retrieve_own_order(test_client):
    phone = f"98{uuid4().int % 100000000:08d}"

    await register_customer(test_client, phone)
    token = await login_customer(test_client, phone)
    address_id = await create_address(test_client, token)
    dish_id = await create_test_dish()

    create_response = await create_order(
        test_client,
        token,
        address_id,
        dish_id
    )

    assert create_response.status_code == 200

    order_id = create_response.json()["id"]

    response = await test_client.get(
        f"/orders/{order_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200, response.text
    assert response.json()["id"] == order_id


async def test_customer_can_cancel_own_placed_order(test_client):
    _, token, order = await prepare_customer_order(test_client)

    response = await test_client.patch(
        f"/orders/{order['id']}/cancel",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200, response.text
    assert response.json()["status"] == "CANCELLED"
    cancellation_notification = await database["notifications"].find_one({
        "order_id": ObjectId(order["id"]),
        "title": "Order Cancelled"
    })
    assert cancellation_notification is not None
    assert cancellation_notification["read"] is False


@pytest.mark.parametrize(
    "status",
    ["PREPARING", "OUT_FOR_DELIVERY", "DELIVERED", "CANCELLED"]
)
async def test_customer_cannot_cancel_order_after_placed(test_client, status):
    customer_id, token, order = await prepare_customer_order(test_client)
    await database["orders"].update_one(
        {"_id": ObjectId(order["id"])},
        {"$set": {"status": status}}
    )
    if status == "CANCELLED":
        await notification_service.create_notification(
            user_id=customer_id,
            order_id=order["id"],
            title="Order Cancelled",
            message="Your order has been cancelled.",
            notification_type="ORDER_STATUS"
        )

    response = await test_client.patch(
        f"/orders/{order['id']}/cancel",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only placed orders can be cancelled"


async def test_customer_cannot_cancel_another_customers_order(test_client):
    _, _, order = await prepare_customer_order(test_client)
    other_phone = f"98{uuid4().int % 100000000:08d}"
    await register_customer(test_client, other_phone)
    other_token = await login_customer(test_client, other_phone)

    response = await test_client.patch(
        f"/orders/{order['id']}/cancel",
        headers={"Authorization": f"Bearer {other_token}"}
    )

    assert response.status_code == 404


@pytest.mark.parametrize("initial_status", ["PLACED", "PREPARING"])
async def test_admin_can_cancel_placed_or_preparing_order(
    test_client,
    initial_status
):
    _, _, order = await prepare_customer_order(test_client)
    if initial_status == "PREPARING":
        await database["orders"].update_one(
            {"_id": ObjectId(order["id"])},
            {"$set": {"status": initial_status}}
        )
    admin_token = await get_admin_token(test_client)

    response = await test_client.patch(
        f"/orders/admin/{order['id']}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "CANCELLED"}
    )

    assert response.status_code == 200, response.text
    assert response.json()["status"] == "CANCELLED"
    cancellation_notification = await database["notifications"].find_one({
        "order_id": ObjectId(order["id"]),
        "title": "Order Cancelled"
    })
    assert cancellation_notification is not None


async def test_admin_status_changes_create_notifications(test_client):
    _, _, order = await prepare_customer_order(test_client)
    admin_token = await get_admin_token(test_client)

    for status in ["PREPARING", "OUT_FOR_DELIVERY", "DELIVERED"]:
        response = await test_client.patch(
            f"/orders/admin/{order['id']}/status",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"status": status}
        )
        assert response.status_code == 200, response.text

        notification = await database["notifications"].find_one({
            "order_id": ObjectId(order["id"]),
            "title": f"Order {status.replace('_', ' ').title()}"
        })
        assert notification is not None


async def test_concurrent_admin_status_updates_create_one_notification(
    test_client
):
    _, _, order = await prepare_customer_order(test_client)

    results = await asyncio.gather(
        order_service.update_order_status(
            order["id"],
            OrderStatus.PREPARING
        ),
        order_service.update_order_status(
            order["id"],
            OrderStatus.PREPARING
        ),
        return_exceptions=True
    )

    assert sum(not isinstance(result, Exception) for result in results) == 1
    preparing_notifications = await database["notifications"].count_documents({
        "order_id": ObjectId(order["id"]),
        "title": "Order Preparing"
    })
    assert preparing_notifications == 1


@pytest.mark.parametrize(
    ("initial_status", "new_status"),
    [
        ("PLACED", "PREPARING"),
        ("PREPARING", "OUT_FOR_DELIVERY"),
        ("OUT_FOR_DELIVERY", "DELIVERED")
    ]
)
async def test_admin_can_advance_order_through_valid_statuses(
    test_client,
    initial_status,
    new_status
):
    _, _, order = await prepare_customer_order(test_client)
    if initial_status != "PLACED":
        await database["orders"].update_one(
            {"_id": ObjectId(order["id"])},
            {"$set": {"status": initial_status}}
        )
    admin_token = await get_admin_token(test_client)

    response = await test_client.patch(
        f"/orders/admin/{order['id']}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": new_status}
    )

    assert response.status_code == 200, response.text
    assert response.json()["status"] == new_status


@pytest.mark.parametrize(
    ("initial_status", "new_status"),
    [
        ("PLACED", "DELIVERED"),
        ("PREPARING", "PLACED"),
        ("OUT_FOR_DELIVERY", "PREPARING"),
        ("DELIVERED", "PLACED"),
        ("DELIVERED", "PREPARING"),
        ("DELIVERED", "OUT_FOR_DELIVERY"),
        ("DELIVERED", "DELIVERED"),
        ("DELIVERED", "CANCELLED"),
        ("CANCELLED", "PLACED"),
        ("CANCELLED", "PREPARING"),
        ("CANCELLED", "OUT_FOR_DELIVERY"),
        ("CANCELLED", "DELIVERED"),
        ("CANCELLED", "CANCELLED"),
    ]
)
async def test_admin_cannot_make_invalid_status_transition(
    test_client,
    initial_status,
    new_status
):
    _, _, order = await prepare_customer_order(test_client)
    await database["orders"].update_one(
        {"_id": ObjectId(order["id"])},
        {"$set": {"status": initial_status}}
    )
    if initial_status == new_status:
        await notification_service.create_notification(
            user_id=order["customer_id"],
            order_id=order["id"],
            title=f"Order {new_status.replace('_', ' ').title()}",
            message=f"Your order is {new_status.replace('_', ' ').lower()}.",
            notification_type="ORDER_STATUS"
        )
    admin_token = await get_admin_token(test_client)

    response = await test_client.patch(
        f"/orders/admin/{order['id']}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": new_status}
    )

    assert response.status_code == 400, response.text
    saved_order = await database["orders"].find_one({
        "_id": ObjectId(order["id"])
    })
    assert saved_order["status"] == initial_status


async def test_admin_status_update_rejects_unknown_status(test_client):
    _, _, order = await prepare_customer_order(test_client)
    admin_token = await get_admin_token(test_client)

    response = await test_client.patch(
        f"/orders/admin/{order['id']}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "UNKNOWN"}
    )

    assert response.status_code == 422, response.text


class StatusRaceCollection:
    def __init__(self, collection, order_id, racing_status):
        self.collection = collection
        self.order_id = ObjectId(order_id)
        self.racing_status = racing_status

    async def find_one(self, query):
        return await self.collection.find_one(query)

    async def update_one(self, query, update):
        await self.collection.update_one(
            {"_id": self.order_id},
            {"$set": {"status": self.racing_status}}
        )
        return await self.collection.update_one(query, update)


class StatusRaceDatabase:
    def __init__(self, order_id, racing_status):
        self.order_id = order_id
        self.racing_status = racing_status

    def __getitem__(self, collection_name):
        collection = database[collection_name]
        if collection_name == "orders":
            return StatusRaceCollection(
                collection,
                self.order_id,
                self.racing_status
            )
        return collection


async def test_customer_cancellation_rejects_status_race(
    test_client,
    monkeypatch
):
    customer_id, _, order = await prepare_customer_order(test_client)
    monkeypatch.setattr(
        order_service_module,
        "database",
        StatusRaceDatabase(order["id"], "PREPARING")
    )

    with pytest.raises(HTTPException) as error:
        await order_service.cancel_customer_order(order["id"], customer_id)

    assert error.value.status_code == 409
    assert "status changed" in error.value.detail.lower()
    saved_order = await database["orders"].find_one({
        "_id": ObjectId(order["id"])
    })
    assert saved_order["status"] == "PREPARING"


async def test_admin_status_update_rejects_status_race(
    test_client,
    monkeypatch
):
    _, _, order = await prepare_customer_order(test_client)
    monkeypatch.setattr(
        order_service_module,
        "database",
        StatusRaceDatabase(order["id"], "CANCELLED")
    )

    with pytest.raises(HTTPException) as error:
        await order_service.update_order_status(
            order["id"],
            OrderStatus.PREPARING
        )

    assert error.value.status_code == 409
    assert "status changed" in error.value.detail.lower()
    saved_order = await database["orders"].find_one({
        "_id": ObjectId(order["id"])
    })
    assert saved_order["status"] == "CANCELLED"
