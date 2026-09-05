from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

MessagePriority = Literal["low", "normal", "high", "urgent"]
MessageType = Literal[
    "message",
    "request",
    "response",
    "handoff",
    "notification",
]


class ExecutiveMessageCreate(BaseModel):
    sender: str = Field(min_length=1, max_length=100)
    recipient: str = Field(min_length=1, max_length=100)
    subject: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1)
    mission_uid: str | None = Field(default=None, max_length=64)
    conversation_uid: str | None = Field(default=None, max_length=64)
    parent_message_uid: str | None = Field(default=None, max_length=64)
    message_type: MessageType = "message"
    priority: MessagePriority = "normal"
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExecutiveMessageReply(BaseModel):
    sender: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1)
    subject: str | None = Field(default=None, max_length=200)
    message_type: MessageType = "response"
    priority: MessagePriority | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExecutiveMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    message_uid: str
    conversation_uid: str
    mission_uid: str | None
    business_uid: str | None
    sender: str
    recipient: str
    subject: str
    message: str
    message_type: str
    priority: str
    status: str
    is_read: bool
    parent_message_uid: str | None
    metadata: dict[str, Any]
    created_at: datetime
    read_at: datetime | None = None
    updated_at: datetime | None = None


class ExecutiveMessageListResponse(BaseModel):
    count: int
    messages: list[ExecutiveMessageResponse]


class ExecutiveConversationResponse(BaseModel):
    conversation_uid: str
    count: int
    messages: list[ExecutiveMessageResponse]
