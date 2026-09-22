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