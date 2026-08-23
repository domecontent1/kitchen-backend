# app/routes/dashboard.py

from fastapi import APIRouter, Depends

from app.core.auth import require_admin
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard_service import dashboard_service


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get(
    "/",
    response_model=DashboardResponse
)
async def get_dashboard(
    current_user: dict = Depends(require_admin)
):
    return await dashboard_service.get_dashboard()