from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.communication.models import ExecutiveMessage
from app.communication.repository import ExecutiveCommunicationRepository
from app.communication.schemas import ExecutiveMessageCreate, ExecutiveMessageReply


class ExecutiveCommunicationService:
    def __init__(self, db: Session) -> None:
        self._repository = ExecutiveCommunicationRepository(db)

    def send_message(
        self,
        payload: ExecutiveMessageCreate,
        *,
        business_uid: str,
    ) -> ExecutiveMessage:
        return self._repository.create(
            business_uid=business_uid,
            sender=payload.sender,
            recipient=payload.recipient,
            subject=payload.subject,
            message=payload.message,
            mission_uid=payload.mission_uid,
            conversation_uid=payload.conversation_uid,
            parent_message_uid=payload.parent_message_uid,
            message_type=payload.message_type,
            priority=payload.priority,
            metadata=payload.metadata,
        )

    def reply_to_message(
        self,
        message_uid: str,
        payload: ExecutiveMessageReply,
        *,
        business_uid: str,
    ) -> ExecutiveMessage | None:
        parent = self._repository.get_by_uid(
            message_uid,
            business_uid=business_uid,
        )

        if parent is None:
            return None

        subject = payload.subject or self._build_reply_subject(
            parent.subject
        )

        return self._repository.create(
            business_uid=business_uid,
            sender=payload.sender,
            recipient=parent.sender,
            subject=subject,
            message=payload.message,
            mission_uid=parent.mission_uid,
            conversation_uid=parent.conversation_uid,
            parent_message_uid=parent.message_uid,
            message_type=payload.message_type,
            priority=payload.priority or parent.priority,
            metadata=payload.metadata,
        )

    def get_message(
        self,
        message_uid: str,
        *,
        business_uid: str,
    ) -> ExecutiveMessage | None:
        return self._repository.get_by_uid(
            message_uid,
            business_uid=business_uid,
        )

    def list_inbox(
        self,
        recipient: str,
        *,
        business_uid: str,
        **kwargs,
    ) -> list[ExecutiveMessage]:
        return self._repository.list_inbox(
            recipient,
            business_uid=business_uid,
            **kwargs,
        )

    def list_outbox(
        self,
        sender: str,
        *,
        business_uid: str,
        **kwargs,
    ) -> list[ExecutiveMessage]:
        return self._repository.list_outbox(
            sender,
            business_uid=business_uid,
            **kwargs,
        )

    def list_conversation(
        self,
        conversation_uid: str,
        *,
        business_uid: str,
        **kwargs,
    ) -> list[ExecutiveMessage]:
        return self._repository.list_conversation(
            conversation_uid,
            business_uid=business_uid,
            **kwargs,
        )

    def list_mission_messages(
        self,
        mission_uid: str,
        *,
        business_uid: str,
        **kwargs,
    ) -> list[ExecutiveMessage]:
        return self._repository.list_mission_messages(
            mission_uid,
            business_uid=business_uid,
            **kwargs,
        )

    def list_between_executives(
        self,
        executive_a: str,
        executive_b: str,
        *,
        business_uid: str,
        **kwargs,
    ) -> list[ExecutiveMessage]:
        return self._repository.list_between_executives(
            executive_a,
            executive_b,
            business_uid=business_uid,
            **kwargs,
        )

    def mark_as_read(
        self,
        message_uid: str,
        *,
        business_uid: str,
    ) -> ExecutiveMessage | None:
        return self._repository.mark_as_read(
            message_uid,
            business_uid=business_uid,
        )

    def delete_message(
        self,
        message_uid: str,
        *,
        business_uid: str,
    ) -> bool:
        return self._repository.delete(
            message_uid,
            business_uid=business_uid,
        )

    def serialize_message(
        self,
        message: ExecutiveMessage,
    ) -> dict[str, Any]:
        return {
            "id": message.id,
            "message_uid": message.message_uid,
            "conversation_uid": message.conversation_uid,
            "mission_uid": message.mission_uid,
            "business_uid": message.business_uid,
            "sender": message.sender,
            "recipient": message.recipient,
            "subject": message.subject,
            "message": message.message,
            "message_type": message.message_type,
            "priority": message.priority,
            "status": message.status,
            "is_read": message.is_read,
            "parent_message_uid": message.parent_message_uid,
            "metadata": self._repository.deserialize_metadata(
                message
            ),
            "created_at": message.created_at,
            "read_at": message.read_at,
            "updated_at": message.updated_at,
        }

    @staticmethod
    def _build_reply_subject(subject: str) -> str:
        cleaned = subject.strip()
        return (
            cleaned
            if cleaned.lower().startswith("re:")
            else f"Re: {cleaned}"
        )