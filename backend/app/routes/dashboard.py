from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

from app.database.database import (
    get_db,
)
from app.schemas.dashboard import (
    DashboardSummary,
)
from app.services.dashboard_service import (
    get_dashboard_summary,
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "/summary",
    response_model=DashboardSummary,
)
def dashboard_summary(
    db: Session = Depends(get_db),
) -> DashboardSummary:
    return get_dashboard_summary(db)