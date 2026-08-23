# app/services/dish_service.py

from bson import ObjectId

from app.core.database import database


def dish_to_response(dish: dict) -> dict:
    return {
        "id": str(dish["_id"]),
        "name": dish["name"],
        "description": dish["description"],
        "price": dish["price"],
        "active": dish["active"]
    }


class DishService:

    async def create_dish(self, dish_data: dict):
        dish_data["active"] = True

        result = await database["dishes"].insert_one(dish_data)

        return await database["dishes"].find_one(
            {"_id": result.inserted_id}
        )

    async def get_dish(self, dish_id: str):
        return await database["dishes"].find_one(
            {
                "_id": ObjectId(dish_id),
                "active": True
            }
        )

    async def update_dish(
        self,
        dish_id: str,
        dish_data: dict
    ):
        result = await database["dishes"].update_one(
            {"_id": ObjectId(dish_id)},
            {
                "$set": dish_data
            }
        )

        if result.matched_count == 0:
            return None

        return await database["dishes"].find_one(
            {"_id": ObjectId(dish_id)}
        )

    async def deactivate_dish(self, dish_id: str):
        result = await database["dishes"].update_one(
            {"_id": ObjectId(dish_id)},
            {
                "$set": {
                    "active": False
                }
            }
        )

        return result.matched_count

    async def reactivate_dish(self, dish_id: str):
        result = await database["dishes"].update_one(
            {"_id": ObjectId(dish_id)},
            {
                "$set": {
                    "active": True
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

        cursor = database["dishes"].find(
            {
                "active": True
            }
        )

        async for dish in cursor:
            dishes.append(dish)

        return dishes

    async def get_all_dishes(self):
        dishes = []

        cursor = database["dishes"].find({})

        async for dish in cursor:
            dishes.append(dish)

        return dishes


dish_service = DishService()