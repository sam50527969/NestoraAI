from fastapi import APIRouter

from app.schemas.sales_ai import (
    SalesAnalysisRequest,
    SalesAnalysisResponse,
)
from app.services.sales_ai import (
    analyze_lead,
)


router = APIRouter(
    prefix="/sales-ai",
    tags=["Sales AI"],
)


@router.post(
    "/analyze",
    response_model=SalesAnalysisResponse,
)
def analyze_sales_lead(
    request: SalesAnalysisRequest,
):
    return analyze_lead(
        request.lead.model_dump()
    )