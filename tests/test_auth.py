# D:\Github\kitchen\backend\tests\test_auth.py
import uuid

import pytest


@pytest.mark.asyncio
async def test_register_customer(test_client):
    phone = f"9{uuid.uuid4().int % 1000000000:09d}"

    response = await test_client.post("/auth/register", json={
        "name": "Test Customer",
        "phone": phone,
        "password": "TestPassword123"
    })

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Test Customer"
    assert data["phone"] == phone
    assert data["role"] == "CUSTOMER"
    assert data["active"] is True
    assert "id" in data


@pytest.mark.asyncio
async def test_duplicate_phone_registration(test_client):
    phone = f"9{uuid.uuid4().int % 1000000000:09d}"

    payload = {
        "name": "Test Customer",
        "phone": phone,
        "password": "TestPassword123"
    }

    first_response = await test_client.post("/auth/register", json=payload)
    assert first_response.status_code == 200

    second_response = await test_client.post("/auth/register", json=payload)

    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Phone number already registered"


@pytest.mark.asyncio
async def test_login_success(test_client):
    phone = f"9{uuid.uuid4().int % 1000000000:09d}"

    await test_client.post("/auth/register", json={
        "name": "Test Customer",
        "phone": phone,
        "password": "TestPassword123"
    })

    response = await test_client.post("/auth/login", json={
        "phone": phone,
        "password": "TestPassword123"
    })

    assert response.status_code == 200

    data = response.json()

    assert data["token_type"] == "bearer"
    assert data["role"] == "CUSTOMER"
    assert data["access_token"]


@pytest.mark.asyncio
async def test_login_wrong_password(test_client):
    phone = f"9{uuid.uuid4().int % 1000000000:09d}"

    await test_client.post("/auth/register", json={
        "name": "Test Customer",
        "phone": phone,
        "password": "TestPassword123"
    })

    response = await test_client.post("/auth/login", json={
        "phone": phone,
        "password": "WrongPassword123"
    })

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid phone number or password"


@pytest.mark.asyncio
async def test_get_me_requires_authentication(test_client):
    response = await test_client.get("/users/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_authenticated(test_client):
    phone = f"9{uuid.uuid4().int % 1000000000:09d}"

    await test_client.post("/auth/register", json={
        "name": "Test Customer",
        "phone": phone,
        "password": "TestPassword123"
    })

    login_response = await test_client.post("/auth/login", json={
        "phone": phone,
        "password": "TestPassword123"
    })

    token = login_response.json()["access_token"]

    response = await test_client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Test Customer"
    assert data["phone"] == phone
    assert data["role"] == "CUSTOMER"
    assert data["active"] is True


async def create_customer_and_token(test_client, name="Test Customer"):
    phone = f"9{uuid.uuid4().int % 1000000000:09d}"
    registered = await test_client.post("/auth/register", json={
        "name": name,
        "phone": phone,
        "password": "TestPassword123"
    })
    assert registered.status_code == 200
    login = await test_client.post("/auth/login", json={
        "phone": phone,
        "password": "TestPassword123"
    })
    assert login.status_code == 200
    return phone, login.json()["access_token"]


@pytest.mark.asyncio
async def test_update_profile_changes_name_and_keeps_phone_unchanged(test_client):
    phone, token = await create_customer_and_token(test_client)

    response = await test_client.put(
        "/users/me",
        json={"name": "  Updated Customer  ", "phone": "9123456789"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Customer"
    assert response.json()["phone"] == phone


@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["", " ", "   "])
async def test_update_profile_rejects_blank_name(test_client, name):
    _, token = await create_customer_and_token(test_client)

    response = await test_client.put(
        "/users/me",
        json={"name": name},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_customer_cannot_update_another_customers_profile(test_client):
    _, first_token = await create_customer_and_token(test_client, "First Customer")
    _, second_token = await create_customer_and_token(test_client, "Second Customer")

    update = await test_client.put(
        "/users/me",
        json={"name": "Changed First Customer"},
        headers={"Authorization": f"Bearer {first_token}"}
    )
    second_profile = await test_client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {second_token}"}
    )

    assert update.status_code == 200
    assert second_profile.status_code == 200
    assert second_profile.json()["name"] == "Second Customer"


@pytest.mark.asyncio
async def test_update_profile_requires_authentication(test_client):
    response = await test_client.put("/users/me", json={"name": "Updated Name"})

    assert response.status_code == 401
