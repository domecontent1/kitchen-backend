# D:\Github\kitchen\backend\tests\test_dishes.py
import uuid
from datetime import datetime, timezone

import pytest

from app.core.database import database
from app.core.security import hash_password


ADMIN_PHONE = "9999999999"
ADMIN_PASSWORD = "AdminTestPassword123"


async def create_test_admin():
    existing_admin = await database["users"].find_one({
        "phone": ADMIN_PHONE
    })

    if existing_admin is not None:
        return

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


async def register_customer(test_client):
    phone = f"9{uuid.uuid4().int % 1000000000:09d}"

    response = await test_client.post("/auth/register", json={
        "name": "Dish Test Customer",
        "phone": phone,
        "password": "TestPassword123"
    })

    assert response.status_code == 200

    response = await test_client.post("/auth/token", data={
        "username": phone,
        "password": "TestPassword123"
    })

    assert response.status_code == 200

    return response.json()["access_token"]


async def get_admin_token(test_client):
    await create_test_admin()

    response = await test_client.post("/auth/token", data={
        "username": ADMIN_PHONE,
        "password": ADMIN_PASSWORD
    })

    assert response.status_code == 200

    return response.json()["access_token"]


def dish_payload(name="Paneer Test Dish"):
    return {
        "name": name,
        "description": "Test dish description",
        "category": "Main Course",
        "price": 150
    }


@pytest.mark.asyncio
async def test_get_dishes_requires_no_authentication(test_client):
    response = await test_client.get("/dishes/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_customer_can_get_active_dishes(test_client):
    token = await register_customer(test_client)

    response = await test_client.get(
        "/dishes/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_dish_requires_admin(test_client):
    token = await register_customer(test_client)

    response = await test_client.post(
        "/dishes/",
        headers={"Authorization": f"Bearer {token}"},
        json=dish_payload()
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_dish(test_client):
    token = await get_admin_token(test_client)

    response = await test_client.post(
        "/dishes/",
        headers={"Authorization": f"Bearer {token}"},
        json=dish_payload()
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"]
    assert data["name"] == "Paneer Test Dish"
    assert data["description"] == "Test dish description"
    assert data["category"] == "Main Course"
    assert data["price"] == 150
    assert data["active"] is True
    assert data["image_url"] is None


@pytest.mark.asyncio
async def test_update_dish(test_client):
    token = await get_admin_token(test_client)

    create_response = await test_client.post(
        "/dishes/",
        headers={"Authorization": f"Bearer {token}"},
        json=dish_payload("Original Dish")
    )

    assert create_response.status_code == 200

    dish_id = create_response.json()["id"]

    response = await test_client.put(
        f"/dishes/{dish_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Updated Dish",
            "description": "Updated description",
            "category": "Snacks",
            "price": 175
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == dish_id
    assert data["name"] == "Updated Dish"
    assert data["description"] == "Updated description"
    assert data["category"] == "Snacks"
    assert data["price"] == 175


@pytest.mark.asyncio
async def test_deactivate_dish(test_client):
    token = await get_admin_token(test_client)

    create_response = await test_client.post(
        "/dishes/",
        headers={"Authorization": f"Bearer {token}"},
        json=dish_payload("Dish To Deactivate")
    )

    assert create_response.status_code == 200

    dish_id = create_response.json()["id"]

    response = await test_client.delete(
        f"/dishes/{dish_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    dishes_response = await test_client.get("/dishes/")

    assert dishes_response.status_code == 200
    assert all(dish["id"] != dish_id for dish in dishes_response.json())


@pytest.mark.asyncio
async def test_reactivate_dish(test_client):
    token = await get_admin_token(test_client)

    create_response = await test_client.post(
        "/dishes/",
        headers={"Authorization": f"Bearer {token}"},
        json=dish_payload("Dish To Reactivate")
    )

    assert create_response.status_code == 200

    dish_id = create_response.json()["id"]

    deactivate_response = await test_client.delete(
        f"/dishes/{dish_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert deactivate_response.status_code == 200

    response = await test_client.post(
        f"/dishes/{dish_id}/reactivate",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == dish_id
    assert data["active"] is True

    dishes_response = await test_client.get("/dishes/")

    assert dishes_response.status_code == 200
    assert any(dish["id"] == dish_id for dish in dishes_response.json())