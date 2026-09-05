from __future__ import annotations

from datetime import UTC, datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.dependencies import get_current_user
from app.business.access import get_current_business_uid
from app.communication.models import ExecutiveMessage
from app.communication.routes import router as communication_router
from app.database.database import Base, get_db


app = FastAPI()
app.include_router(communication_router)


ATLAS_UID = "atlas-auto-care"
DENTAL_UID = "nestora-dental-clinic"


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    TestingSession = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    db = TestingSession()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(db_session):
    def override_db():
        yield db_session

    def override_user():
        return {
            "uid": "communication-test-user",
            "email": "communication@example.com",
        }

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = override_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def _use_workspace(business_uid: str) -> None:
    app.dependency_overrides[
        get_current_business_uid
    ] = lambda: business_uid


def _send(
    client: TestClient,
    *,
    business_uid: str,
    sender: str = "CEO",
    recipient: str = "CMO",
    subject: str = "Growth plan",
    message: str = "Review the growth plan.",
    mission_uid: str | None = "mission-shared",
    conversation_uid: str | None = "conversation-shared",
    extra: dict | None = None,
):
    _use_workspace(business_uid)

    payload = {
        "sender": sender,
        "recipient": recipient,
        "subject": subject,
        "message": message,
        "mission_uid": mission_uid,
        "conversation_uid": conversation_uid,
    }

    if extra:
        payload.update(extra)

    return client.post(
        "/communication/messages",
        json=payload,
    )


def test_create_uses_active_workspace_and_ignores_spoofed_ownership(
    client,
):
    response = _send(
        client,
        business_uid=ATLAS_UID,
        extra={"business_uid": DENTAL_UID},
    )

    assert response.status_code == 201

    body = response.json()

    assert body["business_uid"] == ATLAS_UID
    assert body["sender"] == "CEO"
    assert body["recipient"] == "CMO"


def test_direct_message_lookup_is_workspace_isolated(client):
    created = _send(
        client,
        business_uid=ATLAS_UID,
    )

    assert created.status_code == 201

    message_uid = created.json()["message_uid"]

    _use_workspace(DENTAL_UID)

    foreign = client.get(
        f"/communication/messages/{message_uid}"
    )

    assert foreign.status_code == 404

    _use_workspace(ATLAS_UID)

    owned = client.get(
        f"/communication/messages/{message_uid}"
    )

    assert owned.status_code == 200
    assert owned.json()["business_uid"] == ATLAS_UID


def test_inbox_and_outbox_are_workspace_isolated(client):
    atlas = _send(
        client,
        business_uid=ATLAS_UID,
        subject="Atlas only",
    )
    dental = _send(
        client,
        business_uid=DENTAL_UID,
        subject="Dental only",
    )

    assert atlas.status_code == 201
    assert dental.status_code == 201

    _use_workspace(ATLAS_UID)

    inbox = client.get("/communication/inbox/CMO")
    outbox = client.get("/communication/outbox/CEO")

    assert inbox.status_code == 200
    assert outbox.status_code == 200

    assert inbox.json()["count"] == 1
    assert outbox.json()["count"] == 1

    assert (
        inbox.json()["messages"][0]["subject"]
        == "Atlas only"
    )
    assert (
        outbox.json()["messages"][0]["subject"]
        == "Atlas only"
    )


def test_conversation_and_mission_queries_are_workspace_isolated(
    client,
):
    atlas = _send(
        client,
        business_uid=ATLAS_UID,
        subject="Atlas conversation",
    )
    dental = _send(
        client,
        business_uid=DENTAL_UID,
        subject="Dental conversation",
    )

    assert atlas.status_code == 201
    assert dental.status_code == 201

    _use_workspace(ATLAS_UID)

    conversation = client.get(
        "/communication/conversations/conversation-shared"
    )
    mission = client.get(
        "/communication/missions/mission-shared/messages"
    )

    assert conversation.status_code == 200
    assert mission.status_code == 200

    assert conversation.json()["count"] == 1
    assert mission.json()["count"] == 1

    assert (
        conversation.json()["messages"][0]["business_uid"]
        == ATLAS_UID
    )
    assert (
        mission.json()["messages"][0]["business_uid"]
        == ATLAS_UID
    )


def test_between_executives_is_workspace_isolated(client):
    atlas = _send(
        client,
        business_uid=ATLAS_UID,
        subject="Atlas executives",
    )
    dental = _send(
        client,
        business_uid=DENTAL_UID,
        subject="Dental executives",
    )

    assert atlas.status_code == 201
    assert dental.status_code == 201

    _use_workspace(ATLAS_UID)

    response = client.get(
        "/communication/between",
        params={
            "executive_a": "CEO",
            "executive_b": "CMO",
        },
    )

    assert response.status_code == 200
    assert response.json()["count"] == 1
    assert (
        response.json()["messages"][0]["subject"]
        == "Atlas executives"
    )


def test_reply_cannot_cross_workspace_boundary(client):
    created = _send(
        client,
        business_uid=ATLAS_UID,
    )

    assert created.status_code == 201

    message_uid = created.json()["message_uid"]

    _use_workspace(DENTAL_UID)

    response = client.post(
        f"/communication/messages/{message_uid}/reply",
        json={
            "sender": "CMO",
            "message": "Foreign reply attempt.",
        },
    )

    assert response.status_code == 404

    _use_workspace(ATLAS_UID)

    response = client.post(
        f"/communication/messages/{message_uid}/reply",
        json={
            "sender": "CMO",
            "message": "Owned reply.",
        },
    )

    assert response.status_code == 201
    assert response.json()["business_uid"] == ATLAS_UID
    assert (
        response.json()["parent_message_uid"]
        == message_uid
    )


def test_mark_read_and_delete_cannot_cross_workspace_boundary(
    client,
):
    created = _send(
        client,
        business_uid=ATLAS_UID,
    )

    assert created.status_code == 201

    message_uid = created.json()["message_uid"]

    _use_workspace(DENTAL_UID)

    read_response = client.patch(
        f"/communication/messages/{message_uid}/read"
    )
    delete_response = client.delete(
        f"/communication/messages/{message_uid}"
    )

    assert read_response.status_code == 404
    assert delete_response.status_code == 404

    _use_workspace(ATLAS_UID)

    read_response = client.patch(
        f"/communication/messages/{message_uid}/read"
    )

    assert read_response.status_code == 200
    assert read_response.json()["is_read"] is True

    delete_response = client.delete(
        f"/communication/messages/{message_uid}"
    )

    assert delete_response.status_code == 200

    missing = client.get(
        f"/communication/messages/{message_uid}"
    )

    assert missing.status_code == 404


def test_legacy_unowned_messages_are_hidden(client, db_session):
    legacy = ExecutiveMessage(
        business_uid=None,
        sender="CEO",
        recipient="CMO",
        subject="Legacy unowned",
        message="This record has no workspace owner.",
        mission_uid="mission-shared",
        conversation_uid="conversation-shared",
        created_at=datetime.now(UTC),
    )

    db_session.add(legacy)
    db_session.commit()
    db_session.refresh(legacy)

    _use_workspace(ATLAS_UID)

    direct = client.get(
        f"/communication/messages/{legacy.message_uid}"
    )
    inbox = client.get("/communication/inbox/CMO")
    conversation = client.get(
        "/communication/conversations/conversation-shared"
    )
    mission = client.get(
        "/communication/missions/mission-shared/messages"
    )

    assert direct.status_code == 404
    assert inbox.status_code == 200
    assert inbox.json()["count"] == 0
    assert conversation.status_code == 200
    assert conversation.json()["count"] == 0
    assert mission.status_code == 200
    assert mission.json()["count"] == 0