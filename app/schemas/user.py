# backend/app/schemas/user.py
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints


class UserRole(str, Enum):
    CUSTOMER = "CUSTOMER"
    ADMIN = "ADMIN"


PhoneNumber = Annotated[
    str,
    StringConstraints(strip_whitespace=True, pattern=r"^[6-9]\d{9}$")]

Password = Annotated[
    str,
    StringConstraints(min_length=8, max_length=128)]


class UserRegister(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    phone: PhoneNumber
    password: Password


class UserLogin(BaseModel):
    phone: PhoneNumber
    password: Password


class UserProfileUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=100)


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


class AdminCustomerResponse(BaseModel):
    id: str
    name: str
    phone: str
    active: bool
    order_count: int
    total_spent: float


class AdminCustomerListResponse(BaseModel):
    items: list[AdminCustomerResponse]
    page: int
    page_size: int
    total: int
    total_pages: int


class AdminCustomerOrderResponse(BaseModel):
    id: str
    status: str
    total_amount: float
    delivery_date: str
    delivery_slot: dict
    created_at: str


class AdminCustomerDetailsResponse(BaseModel):
    id: str
    name: str
    phone: str
    active: bool
    order_count: int
    total_spent: float
    orders: list[AdminCustomerOrderResponse]