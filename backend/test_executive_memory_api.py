import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.business.access import get_current_business_uid
from app.database.database import Base, get_db
from app.memory.models import ExecutiveMemory
from app.memory.routes import router as memory_router


@pytest.fixture()
def memory_api():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    session_factory = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(
        bind=engine,
        tables=[
            ExecutiveMemory.__table__,
        ],
    )

    active_business = {
        "uid": "biz_atlas",
    }

    def override_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    def override_business_uid():
        return active_business["uid"]

    app = FastAPI()
    app.include_router(memory_router)

    app.dependency_overrides[
        get_db
    ] = override_db

    app.dependency_overrides[
        get_current_business_uid
    ] = override_business_uid

    with TestClient(app) as client:
        yield (
            client,
            session_factory,
            active_business,
        )

    app.dependency_overrides.clear()

    Base.metadata.drop_all(
        bind=engine,
        tables=[
            ExecutiveMemory.__table__,
        ],
    )

    engine.dispose()


def test_memory_api_uses_active_workspace(
    memory_api,
):
    client, session_factory, active_business = (
        memory_api
    )

    response = client.post(
        "/memory",
        json={
            "executive": "CEO",
            "category": "strategy",
            "memory": "Atlas-only API memory",
            "importance": 9,
            "source": "api-test",
        },
    )

    assert response.status_code == 201

    atlas = response.json()

    assert atlas["business_uid"] == "biz_atlas"

    active_business["uid"] = "biz_dental"

    response = client.post(
        "/memory",
        json={
            "executive": "CEO",
            "category": "strategy",
            "memory": "Dental-only API memory",
            "importance": 8,
            "source": "api-test",
        },
    )

    assert response.status_code == 201

    dental = response.json()

    assert dental["business_uid"] == "biz_dental"

    response = client.get(
        "/memory",
        params={
            "executive": "CEO",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["count"] == 1
    assert body["memories"][0]["id"] == dental["id"]
    assert (
        body["memories"][0]["business_uid"]
        == "biz_dental"
    )

    active_business["uid"] = "biz_atlas"

    response = client.get(
        "/memory",
        params={
            "executive": "CEO",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["count"] == 1
    assert body["memories"][0]["id"] == atlas["id"]

    # Foreign workspace record must look nonexistent.
    response = client.get(
        f"/memory/{dental['id']}"
    )

    assert response.status_code == 404

    response = client.delete(
        f"/memory/{dental['id']}"
    )

    assert response.status_code == 404

    # Failed foreign delete must not delete the record.
    db = session_factory()

    try:
        assert (
            db.query(ExecutiveMemory)
            .filter(
                ExecutiveMemory.id == dental["id"]
            )
            .first()
            is not None
        )
    finally:
        db.close()


def test_memory_api_hides_legacy_null_rows(
    memory_api,
):
    client, session_factory, active_business = (
        memory_api
    )

    db = session_factory()

    try:
        legacy = ExecutiveMemory(
            business_uid=None,
            executive="CEO",
            category="legacy",
            memory="Legacy unowned API memory",
            importance=10,
            source="legacy-test",
        )

        db.add(legacy)
        db.commit()
        db.refresh(legacy)

        legacy_id = legacy.id

    finally:
        db.close()

    active_business["uid"] = "biz_atlas"

    response = client.get(
        "/memory",
        params={
            "executive": "CEO",
        },
    )

    assert response.status_code == 200

    assert all(
        item["id"] != legacy_id
        for item in response.json()["memories"]
    )

    response = client.get(
        f"/memory/{legacy_id}"
    )

    assert response.status_code == 404

    response = client.delete(
        f"/memory/{legacy_id}"
    )

    assert response.status_code == 404


def test_memory_create_cannot_spoof_business_uid(
    memory_api,
):
    client, _, active_business = memory_api

    active_business["uid"] = "biz_atlas"

    response = client.post(
        "/memory",
        json={
            "business_uid": "biz_dental",
            "executive": "CEO",
            "category": "security",
            "memory": "Attempted ownership spoof",
            "importance": 10,
            "source": "api-test",
        },
    )

    assert response.status_code == 201

    body = response.json()

    # Ownership comes from the authenticated active
    # workspace, never from the request payload.
    assert body["business_uid"] == "biz_atlas"
