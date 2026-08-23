# app/schemas/order.py
from datetime import date, time
from typing import Literal

from pydantic import BaseModel, Field


class OrderItemCreate(BaseModel):
    dish_id: str
    quantity: int = Field(gt=0)


class DeliverySlot(BaseModel):
    start: time
    end: time


class OrderCreate(BaseModel):
    items: list[OrderItemCreate] = Field(min_length=1)
    address_id: str
    delivery_date: date
    delivery_slot: DeliverySlot
    notes: str | None = Field(default=None, max_length=500)


class OrderItemResponse(BaseModel):
    dish_id: str
    name: str
    price: float
    quantity: int
    subtotal: float


class DeliveryAddressResponse(BaseModel):
    label: str
    address_line: str
    landmark: str | None
    town: str
    pincode: str


class OrderCustomerResponse(BaseModel):
    name: str
    phone: str


class CustomerResponse(BaseModel):
    name: str
    phone: str


class OrderResponse(BaseModel):
    id: str
    customer_id: str
    customer: CustomerResponse
    items: list[OrderItemResponse]
    delivery_date: date
    delivery_slot: DeliverySlot
    delivery_address: DeliveryAddressResponse
    total_amount: float
    status: str
    notes: str | None
    created_at: str
    updated_at: str


class OrderStatusUpdate(BaseModel):
    status: Literal[
        "PREPARING",
        "OUT_FOR_DELIVERY",
        "DELIVERED",
        "CANCELLED"
    ]