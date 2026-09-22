
# backend/app/services/dish_service.py
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from bson import ObjectId

from app.core.database import database


DISH_IMAGE_DIR = Path("uploads/dishes")
DISH_IMAGE_DIR.mkdir(parents=True, exist_ok=True)


def dish_to_response(dish: dict) -> dict:
    return {
        "id": str(dish["_id"]),
        "name": dish["name"],
        "category": dish.get("category", "Other"),
        "description": dish["description"],
        "price": dish["price"],
        "active": dish["active"],
        "image_url": dish.get("image_url")
    }


class DishService:
    async def create_dish(self, dish_data: dict):
        now = datetime.now(timezone.utc)

        dish_data = {
            "name": dish_data["name"],
            "description": dish_data["description"],
            "price": dish_data["price"],
            "category": dish_data["category"],
            "active": True,
            "image_url": None,
            "created_at": now,
            "updated_at": now
        }

        result = await database["dishes"].insert_one(dish_data)
        return await database["dishes"].find_one({"_id": result.inserted_id})

    async def get_dish(self, dish_id: str):
        return await database["dishes"].find_one(
            {
                "_id": ObjectId(dish_id),
                "active": True
            }
        )

    async def update_dish(self, dish_id: str, dish_data: dict):
        update_data = {
            "name": dish_data["name"],
            "description": dish_data["description"],
            "category": dish_data["category"],
            "price": dish_data["price"],
            "updated_at": datetime.now(timezone.utc)
        }

        result = await database["dishes"].update_one(
            {"_id": ObjectId(dish_id)},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            return None

        return await database["dishes"].find_one(
            {"_id": ObjectId(dish_id)}
        )

    async def update_dish_image(
        self,
        dish_id: str,
        image_bytes: bytes,
        extension: str
    ):
        dish = await database["dishes"].find_one(
            {"_id": ObjectId(dish_id)}
        )

        if dish is None:
            return None

        filename = f"{uuid4().hex}{extension}"
        file_path = DISH_IMAGE_DIR / filename
        file_path.write_bytes(image_bytes)

        old_image_url = dish.get("image_url")

        await database["dishes"].update_one(
            {"_id": ObjectId(dish_id)},
            {
                "$set": {
                    "image_url": f"/uploads/dishes/{filename}",
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )

        if old_image_url:
            old_filename = Path(old_image_url).name
            old_file_path = DISH_IMAGE_DIR / old_filename

            if old_file_path.exists():
                old_file_path.unlink()

        return await database["dishes"].find_one(
            {"_id": ObjectId(dish_id)}
        )

    async def deactivate_dish(self, dish_id: str):
        result = await database["dishes"].update_one(
            {
                "_id": ObjectId(dish_id),
                "active": True
            },
            {
                "$set": {
                    "active": False,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )

        return result.matched_count

    async def reactivate_dish(self, dish_id: str):
        result = await database["dishes"].update_one(
            {
                "_id": ObjectId(dish_id),
                "active": False
            },
            {
                "$set": {
                    "active": True,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )

        if result.matched_count == 0:
            return None

        return await database["dishes"].find_one(
            {"_id": ObjectId(dish_id)}
        )

    async def get_active_dishes(self):
        dishes = []
        cursor = database["dishes"].find({"active": True}).sort("created_at", -1)

        async for dish in cursor:
            dishes.append(dish)

        return dishes

    async def get_all_dishes(self):
        dishes = []
        cursor = database["dishes"].find({}).sort("created_at", -1)

        async for dish in cursor:
            dishes.append(dish)

        return dishes


dish_service = DishService()

