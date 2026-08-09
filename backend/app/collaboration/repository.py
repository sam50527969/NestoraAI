from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.collaboration.models import (
    CollaborationContribution,
    CollaborationSession,
)


class CollaborationRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create_session(
        self,
        *,
        title: str,
        objective: str,
        mission_uid: str | None,
        owner: str,
        participants: list[str],
        shared_context: dict[str, Any],
    ) -> CollaborationSession:
        record = CollaborationSession(
            title=title,
            objective=objective,
            mission_uid=mission_uid,
            owner=owner,
            participants_json=json.dumps(
                participants,
                default=str,
            ),
            shared_context_json=json.dumps(
                shared_context,
                default=str,
            ),
        )

        self._db.add(record)
        self._db.commit()
        self._db.refresh(record)

        return record

    def get_session(
        self,
        session_uid: str,
    ) -> CollaborationSession | None:
        return (
            self._db.query(CollaborationSession)
            .filter(
                CollaborationSession.session_uid
                == session_uid
            )
            .first()
        )

    def list_sessions(
        self,
        *,
        mission_uid: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[CollaborationSession]:
        query = self._db.query(
            CollaborationSession
        )

        if mission_uid:
            query = query.filter(
                CollaborationSession.mission_uid
                == mission_uid
            )

        if status:
            query = query.filter(
                CollaborationSession.status
                == status
            )

        return (
            query
            .order_by(
                CollaborationSession.created_at.desc()
            )
            .limit(limit)
            .all()
        )

    def add_contribution(
        self,
        *,
        session_uid: str,
        executive: str,
        contribution_type: str,
        content: str,
        metadata: dict[str, Any],
    ) -> CollaborationContribution:
        record = CollaborationContribution(
            session_uid=session_uid,
            executive=executive,
            contribution_type=contribution_type,
            content=content,
            metadata_json=json.dumps(
                metadata,
                default=str,
            ),
        )

        self._db.add(record)

        session = self.get_session(session_uid)

        if session is not None and session.status == "open":
            session.status = "in_progress"

        self._db.commit()
        self._db.refresh(record)

        return record

    def list_contributions(
        self,
        session_uid: str,
    ) -> list[CollaborationContribution]:
        return (
            self._db.query(
                CollaborationContribution
            )
            .filter(
                CollaborationContribution.session_uid
                == session_uid
            )
            .order_by(
                CollaborationContribution.created_at.asc()
            )
            .all()
        )

    def close_session(
        self,
        *,
        session_uid: str,
        decision: str,
        status: str,
    ) -> CollaborationSession | None:
        session = self.get_session(session_uid)

        if session is None:
            return None

        session.final_decision = decision
        session.status = status
        session.closed_at = datetime.now(UTC)

        self._db.commit()
        self._db.refresh(session)

        return session

    def delete_session(
        self,
        session_uid: str,
    ) -> bool:
        session = self.get_session(session_uid)

        if session is None:
            return False

        (
            self._db.query(
                CollaborationContribution
            )
            .filter(
                CollaborationContribution.session_uid
                == session_uid
            )
            .delete(
                synchronize_session=False
            )
        )

        self._db.delete(session)
        self._db.commit()

        return True

    @staticmethod
    def parse_json_object(
        value: str | None,
    ) -> dict[str, Any]:
        try:
            parsed = json.loads(value or "{}")
        except (TypeError, json.JSONDecodeError):
            return {}

        return parsed if isinstance(parsed, dict) else {}

    @staticmethod
    def parse_json_list(
        value: str | None,
    ) -> list[str]:
        try:
            parsed = json.loads(value or "[]")
        except (TypeError, json.JSONDecodeError):
            return []

        if not isinstance(parsed, list):
            return []

        return [
            str(item)
            for item in parsed
            if item is not None
        ]
