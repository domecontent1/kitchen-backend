# backend/app/routes/dishes.py
from bson import ObjectId
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.auth import require_admin
from app.schemas.common import MessageResponse
from app.schemas.dish import DishCreate, DishResponse, DishUpdate
from app.services.dish_service import dish_service, dish_to_response


router = APIRouter(prefix="/dishes", tags=["Dishes"])


MAX_IMAGE_SIZE = 5 * 1024 * 1024

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": (b"\xff\xd8\xff", ".jpg"),
    "image/png": (b"\x89PNG\r\n\x1a\n", ".png"),
    "image/webp": (b"RIFF", ".webp")
}


@router.post("/", response_model=DishResponse)
async def create_dish(
    dish: DishCreate,
    current_user: dict = Depends(require_admin)
):
    created_dish = await dish_service.create_dish(dish.model_dump())
    return dish_to_response(created_dish)


@router.get("/", response_model=list[DishResponse])
async def get_dishes():
    dishes = await dish_service.get_active_dishes()
    return [dish_to_response(dish) for dish in dishes]


@router.get("/admin/all", response_model=list[DishResponse])
async def get_all_dishes(current_user: dict = Depends(require_admin)):
    dishes = await dish_service.get_all_dishes()
    return [dish_to_response(dish) for dish in dishes]


@router.get("/{dish_id}", response_model=DishResponse)
async def get_dish(dish_id: str):
    if not ObjectId.is_valid(dish_id):
        raise HTTPException(status_code=400,
            detail="Invalid dish ID")

    dish = await dish_service.get_dish(dish_id)

    if dish is None:
        raise HTTPException(status_code=404,
            detail="Dish not found")

    return dish_to_response(dish)


@router.put("/{dish_id}", response_model=DishResponse)
async def update_dish(
    dish_id: str,
    dish: DishUpdate,
    current_user: dict = Depends(require_admin)):
    if not ObjectId.is_valid(dish_id):
        raise HTTPException(status_code=400,
            detail="Invalid dish ID")

    updated_dish = await dish_service.update_dish(dish_id,
        dish.model_dump())

    if updated_dish is None:
        raise HTTPException(status_code=404,
            detail="Dish not found")

    return dish_to_response(updated_dish)


@router.put("/{dish_id}/image", response_model=DishResponse)
async def upload_dish_image(
    dish_id: str,
    image: UploadFile = File(...),
    current_user: dict = Depends(require_admin)):
    if not ObjectId.is_valid(dish_id):
        raise HTTPException(status_code=400,
            detail="Invalid dish ID")

    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400,
            detail="Only JPEG, PNG, and WebP images are allowed")

    image_bytes = await image.read()

    if not image_bytes:
        raise HTTPException(status_code=400,
            detail="Image file is empty")

    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400,
            detail="Image size must not exceed 5 MB")

    signature, extension = ALLOWED_IMAGE_TYPES[image.content_type]

    if not image_bytes.startswith(signature):
        raise HTTPException(status_code=400,
            detail="Invalid image file")

    if image.content_type == "image/webp" and image_bytes[8:12] != b"WEBP":
        raise HTTPException(status_code=400,
            detail="Invalid WebP image")

    updated_dish = await dish_service.update_dish_image(
        dish_id, image_bytes, extension)

    if updated_dish is None:
        raise HTTPException(status_code=404,
            detail="Dish not found")

    return dish_to_response(updated_dish)


@router.delete("/{dish_id}", response_model=MessageResponse)
async def deactivate_dish(
    dish_id: str,
    current_user: dict = Depends(require_admin)):
    if not ObjectId.is_valid(dish_id):
        raise HTTPException(status_code=400,
            detail="Invalid dish ID")

    matched_count = await dish_service.deactivate_dish(dish_id)

    if matched_count == 0:
        raise HTTPException(status_code=404,
            detail="Dish not found")

    return {"message": "Dish deactivated successfully"}


@router.patch("/{dish_id}/reactivate", response_model=DishResponse)
async def reactivate_dish(
    dish_id: str,
    current_user: dict = Depends(require_admin)):
    if not ObjectId.is_valid(dish_id):
        raise HTTPException(status_code=400,
            detail="Invalid dish ID")

    reactivated_dish = await dish_service.reactivate_dish(dish_id)

    if reactivated_dish is None:
        raise HTTPException(status_code=404,
            detail="Dish not found")

    return dish_to_response(reactivated_dish)