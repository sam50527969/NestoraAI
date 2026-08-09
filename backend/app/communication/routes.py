from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.communication.schemas import (
    ExecutiveConversationResponse,
    ExecutiveMessageCreate,
    ExecutiveMessageListResponse,
    ExecutiveMessageReply,
    ExecutiveMessageResponse,
)
from app.communication.service import ExecutiveCommunicationService
from app.database.database import get_db

router = APIRouter(prefix="/communication", tags=["Executive Communication"])


def _serialize_list(service, messages):
    return [
        ExecutiveMessageResponse(**service.serialize_message(message))
        for message in messages
    ]


@router.get("/health")
def communication_health() -> dict[str, str]:
    return {"status": "ok", "module": "Executive Communication"}


@router.post(
    "/messages",
    response_model=ExecutiveMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def send_message(
    payload: ExecutiveMessageCreate,
    db: Session = Depends(get_db),
) -> ExecutiveMessageResponse:
    service = ExecutiveCommunicationService(db)
    message = service.send_message(payload)
    return ExecutiveMessageResponse(**service.serialize_message(message))


@router.post(
    "/messages/{message_uid}/reply",
    response_model=ExecutiveMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def reply_to_message(
    message_uid: str,
    payload: ExecutiveMessageReply,
    db: Session = Depends(get_db),
) -> ExecutiveMessageResponse:
    service = ExecutiveCommunicationService(db)
    message = service.reply_to_message(message_uid, payload)
    if message is None:
        raise HTTPException(status_code=404, detail="Executive message not found.")
    return ExecutiveMessageResponse(**service.serialize_message(message))


@router.get("/messages/{message_uid}", response_model=ExecutiveMessageResponse)
def get_message(
    message_uid: str,
    db: Session = Depends(get_db),
) -> ExecutiveMessageResponse:
    service = ExecutiveCommunicationService(db)
    message = service.get_message(message_uid)
    if message is None:
        raise HTTPException(status_code=404, detail="Executive message not found.")
    return ExecutiveMessageResponse(**service.serialize_message(message))


@router.get("/inbox/{recipient}", response_model=ExecutiveMessageListResponse)
def list_inbox(
    recipient: str,
    unread_only: bool = Query(default=False),
    mission_uid: str | None = Query(default=None, max_length=64),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> ExecutiveMessageListResponse:
    service = ExecutiveCommunicationService(db)
    messages = service.list_inbox(
        recipient,
        unread_only=unread_only,
        mission_uid=mission_uid,
        limit=limit,
    )
    serialized = _serialize_list(service, messages)
    return ExecutiveMessageListResponse(count=len(serialized), messages=serialized)


@router.get("/outbox/{sender}", response_model=ExecutiveMessageListResponse)
def list_outbox(
    sender: str,
    mission_uid: str | None = Query(default=None, max_length=64),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> ExecutiveMessageListResponse:
    service = ExecutiveCommunicationService(db)
    messages = service.list_outbox(sender, mission_uid=mission_uid, limit=limit)
    serialized = _serialize_list(service, messages)
    return ExecutiveMessageListResponse(count=len(serialized), messages=serialized)


@router.get(
    "/conversations/{conversation_uid}",
    response_model=ExecutiveConversationResponse,
)
def get_conversation(
    conversation_uid: str,
    limit: int = Query(default=500, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> ExecutiveConversationResponse:
    service = ExecutiveCommunicationService(db)
    messages = service.list_conversation(conversation_uid, limit=limit)
    serialized = _serialize_list(service, messages)
    return ExecutiveConversationResponse(
        conversation_uid=conversation_uid,
        count=len(serialized),
        messages=serialized,
    )


@router.get(
    "/missions/{mission_uid}/messages",
    response_model=ExecutiveMessageListResponse,
)
def list_mission_messages(
    mission_uid: str,
    limit: int = Query(default=500, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> ExecutiveMessageListResponse:
    service = ExecutiveCommunicationService(db)
    messages = service.list_mission_messages(mission_uid, limit=limit)
    serialized = _serialize_list(service, messages)
    return ExecutiveMessageListResponse(count=len(serialized), messages=serialized)


@router.get("/between", response_model=ExecutiveMessageListResponse)
def list_between_executives(
    executive_a: str = Query(min_length=1, max_length=100),
    executive_b: str = Query(min_length=1, max_length=100),
    limit: int = Query(default=200, ge=1, le=500),
    db: Session = Depends(get_db),
) -> ExecutiveMessageListResponse:
    service = ExecutiveCommunicationService(db)
    messages = service.list_between_executives(
        executive_a, executive_b, limit=limit
    )
    serialized = _serialize_list(service, messages)
    return ExecutiveMessageListResponse(count=len(serialized), messages=serialized)


@router.patch(
    "/messages/{message_uid}/read",
    response_model=ExecutiveMessageResponse,
)
def mark_message_as_read(
    message_uid: str,
    db: Session = Depends(get_db),
) -> ExecutiveMessageResponse:
    service = ExecutiveCommunicationService(db)
    message = service.mark_as_read(message_uid)
    if message is None:
        raise HTTPException(status_code=404, detail="Executive message not found.")
    return ExecutiveMessageResponse(**service.serialize_message(message))


@router.delete("/messages/{message_uid}", status_code=status.HTTP_200_OK)
def delete_message(
    message_uid: str,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    service = ExecutiveCommunicationService(db)
    if not service.delete_message(message_uid):
        raise HTTPException(status_code=404, detail="Executive message not found.")
    return {"message": "Executive message deleted successfully."}
