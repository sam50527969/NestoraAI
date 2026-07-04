from fastapi import APIRouter

from app.services.lead_service import get_sample_leads

router = APIRouter(prefix="/leads", tags=["Leads"])


@router.get("")
def get_leads():
    return get_sample_leads()