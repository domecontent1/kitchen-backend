# D:\Github\kitchen\backend\tests\test_addresses.py
import uuid

import pytest


async def register_and_login(test_client):
    phone = f"9{uuid.uuid4().int % 1000000000:09d}"

    register_response = await test_client.post("/auth/register", json={
        "name": "Address Test Customer",
        "phone": phone,
        "password": "TestPassword123"
    })

    assert register_response.status_code == 200

    login_response = await test_client.post("/auth/token", data={
        "username": phone,
        "password": "TestPassword123"
    })

    assert login_response.status_code == 200

    return login_response.json()["access_token"]


@pytest.mark.asyncio
async def test_get_addresses_requires_authentication(test_client):
    response = await test_client.get("/addresses/")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_address(test_client):
    token = await register_and_login(test_client)

    response = await test_client.post(
        "/addresses/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "label": "Home",
            "address_line": "123 Main Street",
            "landmark": "Near Temple",
            "town": "Test Town",
            "pincode": "123456"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["label"] == "Home"
    assert data["address_line"] == "123 Main Street"
    assert data["landmark"] == "Near Temple"
    assert data["town"] == "Test Town"
    assert data["pincode"] == "123456"
    assert data["active"] is True
    assert data["id"]


@pytest.mark.asyncio
async def test_get_user_addresses(test_client):
    token = await register_and_login(test_client)

    create_response = await test_client.post(
        "/addresses/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "label": "Home",
            "address_line": "123 Main Street",
            "landmark": None,
            "town": "Test Town",
            "pincode": "123456"
        }
    )

    assert create_response.status_code == 200

    response = await test_client.get(
        "/addresses/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["label"] == "Home"


@pytest.mark.asyncio
async def test_update_address(test_client):
    token = await register_and_login(test_client)

    create_response = await test_client.post(
        "/addresses/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "label": "Home",
            "address_line": "123 Main Street",
            "landmark": None,
            "town": "Test Town",
            "pincode": "123456"
        }
    )

    assert create_response.status_code == 200

    address_id = create_response.json()["id"]

    response = await test_client.put(
        f"/addresses/{address_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "label": "Work",
            "address_line": "456 Market Road",
            "landmark": "Near Bank",
            "town": "New Town",
            "pincode": "654321"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == address_id
    assert data["label"] == "Work"
    assert data["address_line"] == "456 Market Road"
    assert data["landmark"] == "Near Bank"
    assert data["town"] == "New Town"
    assert data["pincode"] == "654321"


@pytest.mark.asyncio
async def test_delete_address(test_client):
    token = await register_and_login(test_client)

    create_response = await test_client.post(
        "/addresses/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "label": "Home",
            "address_line": "123 Main Street",
            "landmark": None,
            "town": "Test Town",
            "pincode": "123456"
        }
    )

    assert create_response.status_code == 200

    address_id = create_response.json()["id"]

    delete_response = await test_client.delete(
        f"/addresses/{address_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert delete_response.status_code == 200

    get_response = await test_client.get(
        "/addresses/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert get_response.status_code == 200
    assert get_response.json() == []