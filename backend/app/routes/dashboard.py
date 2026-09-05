from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

from app.business.access import (
    get_current_business_uid,
)
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
    business_uid: str = Depends(
        get_current_business_uid
    ),
) -> DashboardSummary:
    return get_dashboard_summary(
        db,
        business_uid=business_uid,
    )