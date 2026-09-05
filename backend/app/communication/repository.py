from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.communication.models import ExecutiveMessage


class ExecutiveCommunicationRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(
        self,
        *,
        business_uid: str,
        sender: str,
        recipient: str,
        subject: str,
        message: str,
        mission_uid: str | None = None,
        conversation_uid: str | None = None,
        parent_message_uid: str | None = None,
        message_type: str = "message",
        priority: str = "normal",
        metadata: dict[str, Any] | None = None,
    ) -> ExecutiveMessage:
        record = ExecutiveMessage(
            business_uid=business_uid,
            sender=sender,
            recipient=recipient,
            subject=subject,
            message=message,
            mission_uid=mission_uid,
            parent_message_uid=parent_message_uid,
            message_type=message_type,
            priority=priority,
            metadata_json=json.dumps(metadata or {}, default=str),
        )
        if conversation_uid:
            record.conversation_uid = conversation_uid

        self._db.add(record)
        self._db.commit()
        self._db.refresh(record)
        return record

    def get_by_uid(
        self,
        message_uid: str,
        *,
        business_uid: str,
    ) -> ExecutiveMessage | None:
        return (
            self._db.query(ExecutiveMessage)
            .filter(
                ExecutiveMessage.message_uid == message_uid,
                ExecutiveMessage.business_uid == business_uid,
            )
            .first()
        )

    def list_inbox(
        self,
        recipient: str,
        *,
        business_uid: str,
        unread_only: bool = False,
        mission_uid: str | None = None,
        limit: int = 100,
    ) -> list[ExecutiveMessage]:
        query = self._db.query(ExecutiveMessage).filter(
            ExecutiveMessage.business_uid == business_uid,
            ExecutiveMessage.recipient == recipient,
        )
        if unread_only:
            query = query.filter(ExecutiveMessage.is_read.is_(False))
        if mission_uid:
            query = query.filter(ExecutiveMessage.mission_uid == mission_uid)
        return (
            query.order_by(ExecutiveMessage.created_at.desc())
            .limit(limit)
            .all()
        )

    def list_outbox(
        self,
        sender: str,
        *,
        business_uid: str,
        mission_uid: str | None = None,
        limit: int = 100,
    ) -> list[ExecutiveMessage]:
        query = self._db.query(ExecutiveMessage).filter(
            ExecutiveMessage.business_uid == business_uid,
            ExecutiveMessage.sender == sender,
        )
        if mission_uid:
            query = query.filter(ExecutiveMessage.mission_uid == mission_uid)
        return (
            query.order_by(ExecutiveMessage.created_at.desc())
            .limit(limit)
            .all()
        )

    def list_conversation(
        self,
        conversation_uid: str,
        *,
        business_uid: str,
        limit: int = 500,
    ) -> list[ExecutiveMessage]:
        return (
            self._db.query(ExecutiveMessage)
            .filter(
                ExecutiveMessage.conversation_uid == conversation_uid,
                ExecutiveMessage.business_uid == business_uid,
            )
            .order_by(ExecutiveMessage.created_at.asc())
            .limit(limit)
            .all()
        )

    def list_mission_messages(
        self,
        mission_uid: str,
        *,
        business_uid: str,
        limit: int = 500,
    ) -> list[ExecutiveMessage]:
        return (
            self._db.query(ExecutiveMessage)
            .filter(
                ExecutiveMessage.mission_uid == mission_uid,
                ExecutiveMessage.business_uid == business_uid,
            )
            .order_by(ExecutiveMessage.created_at.asc())
            .limit(limit)
            .all()
        )

    def list_between_executives(
        self,
        executive_a: str,
        executive_b: str,
        *,
        business_uid: str,
        limit: int = 200,
    ) -> list[ExecutiveMessage]:
        return (
            self._db.query(ExecutiveMessage)
            .filter(
                ExecutiveMessage.business_uid == business_uid,
                or_(
                    and_(
                        ExecutiveMessage.sender == executive_a,
                        ExecutiveMessage.recipient == executive_b,
                    ),
                    and_(
                        ExecutiveMessage.sender == executive_b,
                        ExecutiveMessage.recipient == executive_a,
                    ),
                )
            )
            .order_by(ExecutiveMessage.created_at.asc())
            .limit(limit)
            .all()
        )

    def mark_as_read(
        self,
        message_uid: str,
        *,
        business_uid: str,
    ) -> ExecutiveMessage | None:
        record = self.get_by_uid(
            message_uid,
            business_uid=business_uid,
        )
        if record is None:
            return None
        if not record.is_read:
            record.is_read = True
            record.status = "read"
            record.read_at = datetime.now(UTC)
            self._db.commit()
            self._db.refresh(record)
        return record

    def delete(
        self,
        message_uid: str,
        *,
        business_uid: str,
    ) -> bool:
        record = self.get_by_uid(
            message_uid,
            business_uid=business_uid,
        )
        if record is None:
            return False
        self._db.delete(record)
        self._db.commit()
        return True

    @staticmethod
    def deserialize_metadata(record: ExecutiveMessage) -> dict[str, Any]:
        try:
            value = json.loads(record.metadata_json or "{}")
        except (TypeError, json.JSONDecodeError):
            return {}
        return value if isinstance(value, dict) else {}
