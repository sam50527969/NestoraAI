import warnings
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

from app.business.access import get_current_business_uid
from app.database.database import (
    Base,
    get_db,
)
from app.database.models import Business, Lead
from app.routes.ceo import router as ceo_router


warnings.filterwarnings(
    "ignore",
    message=(
        "Using `httpx` with "
        "`starlette.testclient` "
        "is deprecated.*"
    ),
    category=Warning,
)


@pytest.fixture
def ceo_environment(
    tmp_path: Path,
) -> Generator[
    tuple[TestClient, sessionmaker],
    None,
    None,
]:
    database_path = (
        tmp_path
        / "nestora-ceo-test.db"
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
        bind=engine
    )

    with session_factory() as setup_db:
        setup_db.add(
            Business(
                business_uid="biz_atlas",
                name="Atlas Test Business",
                industry="other",
                country="United Arab Emirates",
                currency="AED",
            )
        )
        setup_db.commit()

    app = FastAPI()
    app.include_router(ceo_router)

    def override_get_db():
        db: Session = session_factory()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[
        get_db
    ] = override_get_db

    app.dependency_overrides[
        get_current_business_uid
    ] = lambda: "biz_atlas"

    with TestClient(app) as client:
        yield client, session_factory

    app.dependency_overrides.clear()

    Base.metadata.drop_all(
        bind=engine
    )
    engine.dispose()


def add_lead(
    session_factory,
    *,
    name: str,
    status: str,
    priority: str,
    estimated_value: int | None,
    ai_score: int | None,
) -> None:
    db: Session = session_factory()

    try:
        db.add(
            Lead(
                name=name,
                category="clinic",
                status=status,
                priority=priority,
                business_uid="biz_atlas",
                estimated_value=estimated_value,
                ai_score=ai_score,
            )
        )
        db.commit()
    finally:
        db.close()


def test_ceo_ask_returns_executive_analysis(
    ceo_environment,
):
    client, session_factory = ceo_environment

    add_lead(
        session_factory,
        name="Priority Clinic",
        status="Qualified",
        priority="High",
        estimated_value=50000,
        ai_score=90,
    )

    response = client.post(
        "/ceo/ask",
        json={
            "question": (
                "What should I focus on "
                "to increase revenue?"
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "answer" in data
    assert isinstance(data["answer"], str)
    assert data["answer"].strip()

    assert (
        "50000"
        in data["answer"]
        or "high-priority"
        in data["answer"].lower()
        or "revenue"
        in data["answer"].lower()
    )


def test_ceo_ask_handles_empty_business_state(
    ceo_environment,
):
    client, _ = ceo_environment

    response = client.post(
        "/ceo/ask",
        json={
            "question": (
                "What should the business "
                "focus on today?"
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "answer" in data
    assert isinstance(data["answer"], str)
    assert data["answer"].strip()


def test_ceo_ask_requires_question(
    ceo_environment,
):
    client, _ = ceo_environment

    response = client.post(
        "/ceo/ask",
        json={},
    )

    assert response.status_code == 422


def test_ceo_ask_names_highest_priority_workspace_lead(
    ceo_environment,
):
    client, session_factory = ceo_environment

    add_lead(
        session_factory,
        name="Savant Coffee Shop",
        status="Contacted",
        priority="Medium",
        estimated_value=12000,
        ai_score=72,
    )

    add_lead(
        session_factory,
        name="Atlas Priority Lead",
        status="Qualified",
        priority="High",
        estimated_value=25000,
        ai_score=91,
    )

    with session_factory() as db:
        db.add(
            Lead(
                name="Other Workspace Lead",
                category="clinic",
                status="Qualified",
                priority="Critical",
                business_uid="biz_other",
                estimated_value=99999,
                ai_score=100,
            )
        )
        db.commit()

    response = client.post(
        "/ceo/ask",
        json={
            "question": (
                "What is my highest priority CRM lead "
                "and what should I do next?"
            ),
        },
    )

    assert response.status_code == 200

    answer = response.json()["answer"]

    assert "Atlas Priority Lead" in answer
    assert "Other Workspace Lead" not in answer
    assert "Qualified" in answer
    assert "91" in answer
