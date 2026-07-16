import asyncio

from fastapi import APIRouter, HTTPException

from app.schemas.mission import MissionRequest, MissionStatus
from app.services.mission_manager import (
    create_mission,
    get_mission,
    run_real_mission,
)


router = APIRouter(
    prefix="/missions",
    tags=["Missions"],
)


@router.post("/start", response_model=MissionStatus)
async def start_mission(request: MissionRequest):
    mission = create_mission()

    asyncio.create_task(
        run_real_mission(
            mission["mission_id"],
            request,
        )
    )

    return mission


@router.get("/{mission_id}", response_model=MissionStatus)
async def mission_status(mission_id: str):
    mission = get_mission(mission_id)

    if mission is None:
        raise HTTPException(
            status_code=404,
            detail="Mission not found. Use the complete Mission ID.",
        )

    return mission