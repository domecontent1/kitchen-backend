# app/routes/dishes.py

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import require_admin
from app.schemas.common import MessageResponse
from app.schemas.dish import (
    DishCreate,
    DishUpdate,
    DishResponse
)
from app.services.dish_service import (
    dish_service,
    dish_to_response
)


router = APIRouter(
    prefix="/dishes",
    tags=["Dishes"]
)


@router.post(
    "/",
    response_model=DishResponse
)
async def create_dish(
    dish: DishCreate,
    current_user: dict = Depends(require_admin)
):
    dish_data = dish.model_dump()

    created_dish = await dish_service.create_dish(
        dish_data
    )

    return dish_to_response(created_dish)


@router.get(
    "/",
    response_model=list[DishResponse]
)
async def get_dishes():
    dishes = await dish_service.get_active_dishes()

    return [
        dish_to_response(dish)
        for dish in dishes
    ]


@router.get(
    "/admin/all",
    response_model=list[DishResponse]
)
async def get_all_dishes(
    current_user: dict = Depends(require_admin)
):
    dishes = await dish_service.get_all_dishes()

    return [
        dish_to_response(dish)
        for dish in dishes
    ]


@router.get(
    "/{dish_id}",
    response_model=DishResponse
)
async def get_dish(dish_id: str):

    if not ObjectId.is_valid(dish_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid dish ID"
        )

    dish = await dish_service.get_dish(dish_id)

    if dish is None:
        raise HTTPException(
            status_code=404,
            detail="Dish not found"
        )

    return dish_to_response(dish)


@router.put(
    "/{dish_id}",
    response_model=DishResponse
)
async def update_dish(
    dish_id: str,
    dish: DishUpdate,
    current_user: dict = Depends(require_admin)
):
    if not ObjectId.is_valid(dish_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid dish ID"
        )

    dish_data = dish.model_dump()

    updated_dish = await dish_service.update_dish(
        dish_id,
        dish_data
    )

    if updated_dish is None:
        raise HTTPException(
            status_code=404,
            detail="Dish not found"
        )

    return dish_to_response(updated_dish)


@router.delete(
    "/{dish_id}",
    response_model=MessageResponse
)
async def deactivate_dish(
    dish_id: str,
    current_user: dict = Depends(require_admin)
):
    if not ObjectId.is_valid(dish_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid dish ID"
        )

    matched_count = await dish_service.deactivate_dish(
        dish_id
    )

    if matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Dish not found"
        )

    return {
        "message": "Dish deactivated successfully"
    }


@router.patch(
    "/{dish_id}/reactivate",
    response_model=DishResponse
)
async def reactivate_dish(
    dish_id: str,
    current_user: dict = Depends(require_admin)
):
    if not ObjectId.is_valid(dish_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid dish ID"
        )

    reactivated_dish = await dish_service.reactivate_dish(
        dish_id
    )

    if reactivated_dish is None:
        raise HTTPException(
            status_code=404,
            detail="Dish not found"
        )

    return dish_to_response(reactivated_dish)