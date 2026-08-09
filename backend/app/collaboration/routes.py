from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.collaboration.schemas import (
    CollaborationContributionCreate,
    CollaborationContributionResponse,
    CollaborationDecisionCreate,
    CollaborationSessionCreate,
    CollaborationSessionDetailResponse,
    CollaborationSessionListResponse,
    CollaborationSessionResponse,
)
from app.collaboration.service import (
    CollaborationService,
)
from app.database.database import get_db


router = APIRouter(
    prefix="/collaboration",
    tags=["Executive Collaboration"],
)


@router.get("/health")
def collaboration_health() -> dict[str, str]:
    return {
        "status": "ok",
        "module": "Executive Collaboration",
    }


@router.post(
    "/sessions",
    response_model=CollaborationSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_session(
    payload: CollaborationSessionCreate,
    db: Session = Depends(get_db),
) -> CollaborationSessionResponse:
    service = CollaborationService(db)

    session = service.create_session(payload)

    return CollaborationSessionResponse(
        **service.serialize_session(session)
    )


@router.get(
    "/sessions",
    response_model=CollaborationSessionListResponse,
)
def list_sessions(
    mission_uid: str | None = Query(
        default=None,
        max_length=64,
    ),
    status_filter: str | None = Query(
        default=None,
        alias="status",
        max_length=30,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    db: Session = Depends(get_db),
) -> CollaborationSessionListResponse:
    service = CollaborationService(db)

    sessions = service.list_sessions(
        mission_uid=mission_uid,
        status=status_filter,
        limit=limit,
    )

    serialized = [
        CollaborationSessionResponse(
            **service.serialize_session(session)
        )
        for session in sessions
    ]

    return CollaborationSessionListResponse(
        count=len(serialized),
        sessions=serialized,
    )


@router.get(
    "/sessions/{session_uid}",
    response_model=CollaborationSessionDetailResponse,
)
def get_session(
    session_uid: str,
    db: Session = Depends(get_db),
) -> CollaborationSessionDetailResponse:
    service = CollaborationService(db)

    session = service.get_session(session_uid)

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collaboration session not found.",
        )

    contributions = service.list_contributions(
        session_uid
    )

    serialized_contributions = [
        CollaborationContributionResponse(
            **service.serialize_contribution(
                contribution
            )
        )
        for contribution in contributions
    ]

    return CollaborationSessionDetailResponse(
        session=CollaborationSessionResponse(
            **service.serialize_session(session)
        ),
        contribution_count=len(
            serialized_contributions
        ),
        contributions=serialized_contributions,
    )


@router.post(
    "/sessions/{session_uid}/contributions",
    response_model=CollaborationContributionResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_contribution(
    session_uid: str,
    payload: CollaborationContributionCreate,
    db: Session = Depends(get_db),
) -> CollaborationContributionResponse:
    service = CollaborationService(db)

    contribution = service.add_contribution(
        session_uid,
        payload,
    )

    if contribution is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collaboration session not found.",
        )

    return CollaborationContributionResponse(
        **service.serialize_contribution(
            contribution
        )
    )


@router.post(
    "/sessions/{session_uid}/decision",
    response_model=CollaborationSessionResponse,
)
def close_session(
    session_uid: str,
    payload: CollaborationDecisionCreate,
    db: Session = Depends(get_db),
) -> CollaborationSessionResponse:
    service = CollaborationService(db)

    session = service.close_session(
        session_uid,
        payload,
    )

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collaboration session not found.",
        )

    return CollaborationSessionResponse(
        **service.serialize_session(session)
    )


@router.delete(
    "/sessions/{session_uid}",
    status_code=status.HTTP_200_OK,
)
def delete_session(
    session_uid: str,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    service = CollaborationService(db)

    deleted = service.delete_session(session_uid)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collaboration session not found.",
        )

    return {
        "message": (
            "Collaboration session deleted successfully."
        ),
    }
