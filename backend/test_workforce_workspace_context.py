import asyncio

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.auth.dependencies import get_current_user
from app.business.access import get_current_business_uid
from app.realtime.connection_manager import ConnectionManager
from app.realtime.router import router
from app.realtime.workforce_registry import (
    WorkforceRegistry,
    workforce_registry,
)


class FakeWebSocket:
    def __init__(self) -> None:
        self.messages = []

    async def send_json(self, message) -> None:
        self.messages.append(message)


def test_workforce_registry_is_separate_per_workspace():
    registry = WorkforceRegistry()

    registry.update(
        "biz_one",
        "sales",
        status="running",
        task="Prepare proposal",
        progress=50,
    )

    one = registry.get("biz_one", "sales")
    two = registry.get("biz_two", "sales")

    assert one["status"] == "running"
    assert one["current_task"] == "Prepare proposal"
    assert two["status"] == "idle"
    assert two["current_task"] is None


def test_broadcast_only_reaches_same_workspace():
    manager = ConnectionManager()
    one = FakeWebSocket()
    two = FakeWebSocket()

    manager.register(one, "biz_one")
    manager.register(two, "biz_two")

    event = {"event": "workforce.updated"}
    asyncio.run(
        manager.broadcast(event, "biz_one")
    )

    assert one.messages == [event]
    assert two.messages == []


def test_workforce_http_state_is_workspace_scoped():
    app = FastAPI()
    app.include_router(router)
    selected = {"business_uid": "biz_one"}

    app.dependency_overrides[
        get_current_user
    ] = lambda: object()
    app.dependency_overrides[
        get_current_business_uid
    ] = lambda: selected["business_uid"]

    workforce_registry.clear()

    with TestClient(app) as client:
        response = client.post(
            "/realtime/workforce/update",
            json={
                "executive": "sales",
                "status": "running",
                "task": "Prepare proposal",
                "progress": 50,
            },
        )
        assert response.status_code == 200

        selected["business_uid"] = "biz_two"
        response = client.get(
            "/realtime/workforce"
        )

    assert response.status_code == 200
    sales = next(
        item
        for item in response.json()["executives"]
        if item["department"] == "Sales"
    )
    assert sales["status"] == "idle"
    assert sales["current_task"] is None

    workforce_registry.clear()
