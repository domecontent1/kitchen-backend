# backend/app/schemas/order.py
from datetime import date, time
from typing import Optional

from pydantic import BaseModel, Field

from app.core.enums import OrderStatus


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
    notes: Optional[str] = Field(default=None, max_length=500)


class OrderItemResponse(BaseModel):
    dish_id: str
    name: str
    price: float
    quantity: int
    subtotal: float


class DeliveryAddressResponse(BaseModel):
    label: str
    address_line: str
    landmark: Optional[str]
    town: str
    pincode: str


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
    status: OrderStatus
    notes: Optional[str]
    created_at: str
    updated_at: str


class AdminOrderListResponse(BaseModel):
    items: list[OrderResponse]
    page: int
    page_size: int
    total: int
    total_pages: int


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class AdminOrderStatusCounts(BaseModel):
    ALL: int
    PLACED: int
    PREPARING: int
    OUT_FOR_DELIVERY: int
    DELIVERED: int
    CANCELLED: int