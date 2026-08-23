from fastapi import APIRouter, Depends

from app.core.auth import get_current_user
from app.schemas.user import UserResponse


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get(
    "/me",
    response_model=UserResponse
)
async def get_me(
    current_user: dict = Depends(get_current_user)
):

    return {
        "id": str(current_user["_id"]),
        "name": current_user["name"],
        "phone": current_user["phone"],
        "role": current_user["role"],
        "active": current_user["active"]
    }