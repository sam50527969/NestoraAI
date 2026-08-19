from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import (
    Session,
    sessionmaker,
)
from starlette.websockets import (
    WebSocketDisconnect,
)

from app.auth.models import User
from app.auth.security import (
    create_access_token,
    hash_password,
)
from app.database.database import (
    Base,
    get_db,
)
from app.realtime.connection_manager import (
    connection_manager,
)
from app.realtime.router import (
    router as realtime_router,
)


@pytest.fixture
def realtime_environment(
    tmp_path: Path,
) -> Generator[
    tuple[TestClient, sessionmaker],
    None,
    None,
]:
    database_path = (
        tmp_path
        / "nestora-realtime-test.db"
    )

    engine = create_engine(
        f"sqlite:///{database_path}",
        connect_args={
            "check_same_thread": False,
        },
    )

    session_factory = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(
        bind=engine,
    )

    app = FastAPI()
    app.include_router(
        realtime_router,
    )

    def override_get_db():
        db: Session = session_factory()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[
        get_db
    ] = override_get_db

    connection_manager.active_connections.clear()

    with TestClient(app) as client:
        yield client, session_factory

    connection_manager.active_connections.clear()
    app.dependency_overrides.clear()

    Base.metadata.drop_all(
        bind=engine,
    )

    engine.dispose()


def create_test_user(
    session_factory: sessionmaker,
    *,
    is_active: bool = True,
) -> User:
    with session_factory() as db:
        user = User(
            email="realtime@nestora.test",
            full_name="Realtime User",
            password_hash=hash_password(
                "StrongPassword123!",
            ),
            role="user",
            is_active=is_active,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        db.expunge(user)

        return user


def test_authenticated_socket_receives_snapshot_and_pong(
    realtime_environment,
) -> None:
    client, session_factory = (
        realtime_environment
    )

    user = create_test_user(
        session_factory,
    )

    token, _ = create_access_token(
        user.user_uid,
    )

    with client.websocket_connect(
        "/realtime/workforce",
    ) as websocket:
        websocket.send_json({
            "event": (
                "socket.authenticate"
            ),
            "token": token,
        })

        authenticated = (
            websocket.receive_json()
        )

        assert (
            authenticated["event"]
            == "socket.authenticated"
        )

        assert (
            authenticated["data"][
                "user_uid"
            ]
            == user.user_uid
        )

        snapshot = (
            websocket.receive_json()
        )

        assert (
            snapshot["event"]
            == "workforce.snapshot"
        )

        websocket.send_text("ping")

        pong = websocket.receive_json()

        assert pong["event"] == "pong"


def test_invalid_token_is_rejected(
    realtime_environment,
) -> None:
    client, _ = realtime_environment

    with pytest.raises(
        WebSocketDisconnect,
    ) as error:
        with client.websocket_connect(
            "/realtime/workforce",
        ) as websocket:
            websocket.send_json({
                "event": (
                    "socket.authenticate"
                ),
                "token": "invalid-token",
            })

            websocket.receive_json()

    assert error.value.code == 4401


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {
            "event": "wrong.event",
            "token": "invalid-token",
        },
        {
            "event": (
                "socket.authenticate"
            ),
        },
        {
            "event": (
                "socket.authenticate"
            ),
            "token": 123,
        },
    ],
)
def test_invalid_authentication_message_is_rejected(
    realtime_environment,
    payload: dict,
) -> None:
    client, _ = realtime_environment

    with pytest.raises(
        WebSocketDisconnect,
    ) as error:
        with client.websocket_connect(
            "/realtime/workforce",
        ) as websocket:
            websocket.send_json(payload)
            websocket.receive_json()

    assert error.value.code == 4401


def test_inactive_user_is_rejected(
    realtime_environment,
) -> None:
    client, session_factory = (
        realtime_environment
    )

    user = create_test_user(
        session_factory,
        is_active=False,
    )

    token, _ = create_access_token(
        user.user_uid,
    )

    with pytest.raises(
        WebSocketDisconnect,
    ) as error:
        with client.websocket_connect(
            "/realtime/workforce",
        ) as websocket:
            websocket.send_json({
                "event": (
                    "socket.authenticate"
                ),
                "token": token,
            })

            websocket.receive_json()

    assert error.value.code == 4401