from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import (
    create_access_token,
    verify_password
)

from app.schemas.user import (
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse
)

from app.services.user_service import user_service


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse
)
async def register_user(user: UserRegister):

    existing_user = await user_service.get_user_by_phone(
        user.phone
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=409,
            detail="Phone number already registered"
        )

    created_user = await user_service.create_customer(
        name=user.name,
        phone=user.phone,
        password=user.password
    )

    return {
        "id": str(created_user["_id"]),
        "name": created_user["name"],
        "phone": created_user["phone"],
        "role": created_user["role"],
        "active": created_user["active"]
    }


@router.post(
    "/login",
    response_model=TokenResponse
)
async def login_user(user: UserLogin):

    existing_user = await user_service.get_user_by_phone(
        user.phone
    )

    if existing_user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid phone number or password"
        )

    if not existing_user["active"]:
        raise HTTPException(
            status_code=403,
            detail="User account is inactive"
        )

    password_valid = verify_password(
        user.password,
        existing_user["password_hash"]
    )

    if not password_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid phone number or password"
        )

    access_token = create_access_token(
        user_id=str(existing_user["_id"]),
        role=existing_user["role"]
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": existing_user["role"]
    }


@router.post(
    "/token",
    include_in_schema=False
)
async def login_for_swagger(
    form_data: OAuth2PasswordRequestForm = Depends()
):

    existing_user = await user_service.get_user_by_phone(
        form_data.username
    )

    if existing_user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid phone number or password"
        )

    if not existing_user["active"]:
        raise HTTPException(
            status_code=403,
            detail="User account is inactive"
        )

    password_valid = verify_password(
        form_data.password,
        existing_user["password_hash"]
    )

    if not password_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid phone number or password"
        )

    access_token = create_access_token(
        user_id=str(existing_user["_id"]),
        role=existing_user["role"]
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": existing_user["role"]
    }