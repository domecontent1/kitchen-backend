# app/routes/orders.py
from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import (
    get_current_user,
    require_admin
)

from app.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderStatusUpdate
)

from app.services.order_service import order_service


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


def order_to_response(order: dict) -> dict:
    return {
        "id": str(order["_id"]),
        "customer_id": str(order["customer_id"]),
        "customer": order["customer"],
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


# ============================================================
# CUSTOMER ROUTES
# ============================================================

@router.post(
    "/",
    response_model=OrderResponse
)
async def create_order(
    order: OrderCreate,
    current_user: dict = Depends(get_current_user)
):
    created_order = await order_service.create_order(
        customer_id=str(current_user["_id"]),
        order_data=order.model_dump()
    )

    return order_to_response(created_order)


@router.get(
    "/",
    response_model=list[OrderResponse]
)
async def get_my_orders(
    current_user: dict = Depends(get_current_user)
):
    orders = await order_service.get_customer_orders(
        customer_id=str(current_user["_id"])
    )

    return [
        order_to_response(order)
        for order in orders
    ]


# ============================================================
# ADMIN ROUTES
# ============================================================

@router.get(
    "/admin/all",
    response_model=list[OrderResponse]
)
async def get_all_orders(
    current_user: dict = Depends(require_admin)
):
    orders = await order_service.get_all_orders()

    return [
        order_to_response(order)
        for order in orders
    ]


@router.get(
    "/admin/{order_id}",
    response_model=OrderResponse
)
async def get_admin_order(
    order_id: str,
    current_user: dict = Depends(require_admin)
):
    orders = await order_service.get_all_orders()

    order = next(
        (
            order
            for order in orders
            if str(order["_id"]) == order_id
        ),
        None
    )

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return order_to_response(order)


@router.patch(
    "/admin/{order_id}/status",
    response_model=OrderResponse
)
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
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return order_to_response(updated_order)


# ============================================================
# CUSTOMER ORDER DETAILS / CANCEL
# ============================================================

@router.get(
    "/{order_id}",
    response_model=OrderResponse
)
async def get_my_order(
    order_id: str,
    current_user: dict = Depends(get_current_user)
):
    order = await order_service.get_order_by_id(
        order_id=order_id,
        customer_id=str(current_user["_id"])
    )

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return order_to_response(order)


@router.patch(
    "/{order_id}/cancel",
    response_model=OrderResponse
)
async def cancel_my_order(
    order_id: str,
    current_user: dict = Depends(get_current_user)
):
    cancelled_order = await order_service.cancel_customer_order(
        order_id=order_id,
        customer_id=str(current_user["_id"])
    )

    if cancelled_order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return order_to_response(cancelled_order)