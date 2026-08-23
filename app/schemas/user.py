from enum import Enum

from pydantic import BaseModel, Field


class UserRole(str, Enum):
    CUSTOMER = "CUSTOMER"
    ADMIN = "ADMIN"


class UserRegister(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100
    )

    phone: str = Field(
        pattern=r"^[6-9]\d{9}$"
    )

    password: str = Field(
        min_length=8,
        max_length=128
    )


class UserLogin(BaseModel):
    phone: str = Field(
        pattern=r"^[6-9]\d{9}$"
    )

    password: str = Field(
        min_length=8,
        max_length=128
    )


class UserResponse(BaseModel):
    id: str
    name: str
    phone: str
    role: UserRole
    active: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: UserRole