# D:\Github\kitchen\backend\tests\test_orders.py
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.core.database import database


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
                "end": "13:00"
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