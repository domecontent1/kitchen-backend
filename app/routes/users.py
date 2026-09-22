# backend/app/routes/users.py
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import get_current_user, require_admin
from app.schemas.user import (
    AdminCustomerDetailsResponse,
    AdminCustomerListResponse,
    AdminCustomerResponse,
    UserProfileUpdate,
    UserResponse
)
from app.services.user_service import user_service


router = APIRouter(prefix="/users", tags=["Users"])


def user_to_response(user: dict) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "phone": user["phone"],
        "role": user["role"],
        "active": user["active"]
    }


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return user_to_response(current_user)


@router.put("/me", response_model=UserResponse)
async def update_me(
    user_data: UserProfileUpdate,
    current_user: dict = Depends(get_current_user)):
    updated_user = await user_service.update_profile(
        user_id=str(current_user["_id"]),
        name=user_data.name)

    if updated_user is None:
        raise HTTPException(status_code=404,
            detail="User not found")

    return user_to_response(updated_user)


@router.get("/customers", response_model=AdminCustomerListResponse)
async def get_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, max_length=100),
    active: Optional[bool] = Query(None),
    current_user: dict = Depends(require_admin)
):
    return await user_service.get_admin_customers(
        page=page,
        page_size=page_size,
        search=search,
        active=active)


@router.get("/customers/{customer_id}", response_model=AdminCustomerDetailsResponse)
async def get_customer_details(
    customer_id: str,
    current_user: dict = Depends(require_admin)):
    customer = await user_service.get_admin_customer_details(customer_id)

    if customer is None:
        raise HTTPException(status_code=404,
            detail="Customer not found")

    return customer