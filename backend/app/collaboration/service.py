from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.collaboration.models import (
    CollaborationContribution,
    CollaborationSession,
)
from app.collaboration.repository import (
    CollaborationRepository,
)
from app.collaboration.schemas import (
    CollaborationContributionCreate,
    CollaborationDecisionCreate,
    CollaborationSessionCreate,
)


class CollaborationService:
    def __init__(self, db: Session) -> None:
        self._repository = CollaborationRepository(db)

    def create_session(
        self,
        payload: CollaborationSessionCreate,
    ) -> CollaborationSession:
        participants = self._normalize_participants(
            owner=payload.owner,
            participants=payload.participants,
        )

        return self._repository.create_session(
            title=payload.title,
            objective=payload.objective,
            mission_uid=payload.mission_uid,
            owner=payload.owner,
            participants=participants,
            shared_context=payload.shared_context,
        )

    def get_session(
        self,
        session_uid: str,
    ) -> CollaborationSession | None:
        return self._repository.get_session(
            session_uid
        )

    def list_sessions(
        self,
        *,
        mission_uid: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[CollaborationSession]:
        return self._repository.list_sessions(
            mission_uid=mission_uid,
            status=status,
            limit=limit,
        )

    def add_contribution(
        self,
        session_uid: str,
        payload: CollaborationContributionCreate,
    ) -> CollaborationContribution | None:
        session = self._repository.get_session(
            session_uid
        )

        if session is None:
            return None

        return self._repository.add_contribution(
            session_uid=session_uid,
            executive=payload.executive,
            contribution_type=(
                payload.contribution_type
            ),
            content=payload.content,
            metadata=payload.metadata,
        )

    def list_contributions(
        self,
        session_uid: str,
    ) -> list[CollaborationContribution]:
        return self._repository.list_contributions(
            session_uid
        )

    def close_session(
        self,
        session_uid: str,
        payload: CollaborationDecisionCreate,
    ) -> CollaborationSession | None:
        session = self._repository.close_session(
            session_uid=session_uid,
            decision=payload.decision,
            status=payload.status,
        )

        if session is None:
            return None

        self._repository.add_contribution(
            session_uid=session_uid,
            executive=payload.executive,
            contribution_type="decision",
            content=payload.decision,
            metadata={
                **payload.metadata,
                "decision_status": payload.status,
            },
        )

        return session

    def delete_session(
        self,
        session_uid: str,
    ) -> bool:
        return self._repository.delete_session(
            session_uid
        )

    def serialize_session(
        self,
        session: CollaborationSession,
    ) -> dict[str, Any]:
        return {
            "id": session.id,
            "session_uid": session.session_uid,
            "mission_uid": session.mission_uid,
            "title": session.title,
            "objective": session.objective,
            "owner": session.owner,
            "status": session.status,
            "participants": (
                self._repository.parse_json_list(
                    session.participants_json
                )
            ),
            "shared_context": (
                self._repository.parse_json_object(
                    session.shared_context_json
                )
            ),
            "final_decision": session.final_decision,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "closed_at": session.closed_at,
        }

    def serialize_contribution(
        self,
        contribution: CollaborationContribution,
    ) -> dict[str, Any]:
        return {
            "id": contribution.id,
            "contribution_uid": (
                contribution.contribution_uid
            ),
            "session_uid": contribution.session_uid,
            "executive": contribution.executive,
            "contribution_type": (
                contribution.contribution_type
            ),
            "content": contribution.content,
            "metadata": (
                self._repository.parse_json_object(
                    contribution.metadata_json
                )
            ),
            "created_at": contribution.created_at,
        }

    @staticmethod
    def _normalize_participants(
        *,
        owner: str,
        participants: list[str],
    ) -> list[str]:
        normalized: list[str] = []

        for participant in [
            owner,
            *participants,
        ]:
            cleaned = str(participant).strip()

            if cleaned and cleaned not in normalized:
                normalized.append(cleaned)

        return normalized
