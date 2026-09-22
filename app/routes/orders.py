from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query

from app.core.auth import get_current_user, require_admin
from app.core.enums import OrderStatus
from app.schemas.order import (
    AdminOrderListResponse,
    AdminOrderStatusCounts,
    OrderCreate,
    OrderResponse,
    OrderStatusUpdate
)
from app.services.order_service import order_service


router = APIRouter(prefix="/orders", tags=["Orders"])


def order_to_response(order: dict) -> dict:
    return {
        "id": str(order["_id"]),
        "customer_id": str(order["customer_id"]),
        "customer": order.get("customer", {
            "name": "Unknown Customer",
            "phone": ""
        }),
        "items": order["items"],
        "delivery_date": order["delivery_date"],
        "delivery_slot": order["delivery_slot"],
        "delivery_address": order["delivery_address"],
        "total_amount": order["total_amount"],
        "status": order["status"],
        "notes": order.get("notes"),
        "created_at": order["created_at"].isoformat(),
        "updated_at": order["updated_at"].isoformat()
    }


# CUSTOMER ROUTES

@router.post("/", response_model=OrderResponse)
async def create_order(
    order: OrderCreate,
    idempotency_key: str = Header(..., alias="X-Idempotency-Key", min_length=1, max_length=100),
    current_user: dict = Depends(get_current_user)
):
    created_order = await order_service.create_order(
        customer_id=str(current_user["_id"]),
        order_data=order.model_dump(),
        idempotency_key=idempotency_key
    )

    return order_to_response(created_order)


@router.get("/", response_model=list[OrderResponse])
async def get_my_orders(current_user: dict = Depends(get_current_user)):
    orders = await order_service.get_customer_orders(
        customer_id=str(current_user["_id"])
    )
    return [order_to_response(order) for order in orders]


# ADMIN ROUTES

@router.get("/admin", response_model=AdminOrderListResponse)
async def get_admin_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[OrderStatus] = Query(None),
    search: Optional[str] = Query(None),
    current_user: dict = Depends(require_admin)
):
    result = await order_service.get_admin_orders(
        page=page,
        page_size=page_size,
        status=status,
        search=search
    )

    return {
        "items": [order_to_response(order) for order in result["items"]],
        "page": result["page"],
        "page_size": result["page_size"],
        "total": result["total"],
        "total_pages": result["total_pages"]
    }


@router.get("/admin/status-counts", response_model=AdminOrderStatusCounts)
async def get_admin_order_status_counts(
    current_user: dict = Depends(require_admin)
):
    return await order_service.get_admin_order_status_counts()


@router.get("/admin/{order_id}", response_model=OrderResponse)
async def get_admin_order(
    order_id: str,
    current_user: dict = Depends(require_admin)
):
    order = await order_service.get_admin_order_by_id(order_id)

    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    return order_to_response(order)


@router.patch("/admin/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: str,
    status_update: OrderStatusUpdate,
    current_user: dict = Depends(require_admin)
):
    updated_order = await order_service.update_order_status(
        order_id=order_id,
        new_status=status_update.status
    )

    if updated_order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    return order_to_response(updated_order)


# CUSTOMER ORDER DETAILS / CANCEL

@router.get("/{order_id}", response_model=OrderResponse)
async def get_my_order(
    order_id: str,
    current_user: dict = Depends(get_current_user)
):
    order = await order_service.get_order_by_id(
        order_id=order_id,
        customer_id=str(current_user["_id"])
    )

    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    return order_to_response(order)


@router.patch("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_my_order(
    order_id: str,
    current_user: dict = Depends(get_current_user)
):
    cancelled_order = await order_service.cancel_customer_order(
        order_id=order_id,
        customer_id=str(current_user["_id"])
    )

    if cancelled_order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    return order_to_response(cancelled_order)