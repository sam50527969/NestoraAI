from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.bootstrap.routes import register_routes
from app.database.database import Base, get_db
from app.auth.models import User
from app.database.models import Business, BusinessMembership


TEST_EMAIL = "business-owner@nestora.test"
TEST_PASSWORD = "StrongPassword123!"


@pytest.fixture
def business_api(
    tmp_path: Path,
) -> Generator[
    tuple[TestClient, sessionmaker],
    None,
    None,
]:
    database_path = (
        tmp_path
        / "nestora-business-onboarding.db"
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

    app = FastAPI()
    register_routes(app)

    def override_get_db():
        db: Session = session_factory()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[
        get_db
    ] = override_get_db

    with TestClient(app) as client:
        yield client, session_factory

    app.dependency_overrides.clear()

    Base.metadata.drop_all(
        bind=engine
    )

    engine.dispose()


def business_payload() -> dict:
    return {
        "name": "Northstar Signage",
        "industry": "other",
        "country": "Australia",
        "city": "Sydney",
        "region": "New South Wales",
        "timezone": "Australia/Sydney",
        "locale": "en-AU",
        "size": "small",
        "description": (
            "Commercial signage and "
            "visual branding company."
        ),
        "team": {
            "employees": 8,
            "departments": [
                "Sales",
                "Production",
            ],
        },
        "customers": {
            "target_segments": [
                "Retail businesses",
                "Corporate clients",
            ],
            "average_customer_value": 2500,
            "acquisition_channels": [
                "Referrals",
                "Search",
            ],
        },
        "finances": {
            "monthly_revenue": 50000,
            "monthly_expenses": 30000,
            "cash_balance": 75000,
            "currency": "AUD",
        },
        "operations": {
            "working_hours": [
                {
                    "day": "monday",
                    "open_time": "08:00",
                    "close_time": "17:00",
                },
            ],
            "working_days": [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
            ],
            "capacity": 100,
            "current_utilization": 60,
        },
        "goals": [
            "Increase qualified leads",
        ],
        "metadata": {},
    }


def register_and_login(
    client: TestClient,
) -> tuple[str, str]:
    registration = client.post(
        "/auth/register",
        json={
            "email": TEST_EMAIL,
            "full_name":
                "Business Owner",
            "password":
                TEST_PASSWORD,
        },
    )

    assert registration.status_code == 201

    login = client.post(
        "/auth/login",
        json={
            "email": TEST_EMAIL,
            "password":
                TEST_PASSWORD,
        },
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    return token, TEST_EMAIL


def test_business_creation_requires_authentication(
    business_api,
) -> None:
    client, _session_factory = (
        business_api
    )

    response = client.post(
        "/businesses",
        json=business_payload(),
    )

    assert response.status_code == 401


def test_authenticated_creation_creates_owner_membership(
    business_api,
) -> None:
    client, session_factory = (
        business_api
    )

    token, email = register_and_login(
        client
    )

    response = client.post(
        "/businesses",
        json=business_payload(),
        headers={
            "Authorization":
                f"Bearer {token}",
        },
    )


    assert response.status_code == 201

    body = response.json()

    business_uid = body[
        "business_uid"
    ]

    assert business_uid.startswith("biz_")
    assert body["name"] == (
        "Northstar Signage"
    )
    assert body["country"] == (
        "Australia"
    )
    assert body["city"] == "Sydney"
    assert body["finances"]["currency"] == "AUD"

    db: Session = session_factory()

    try:
        user = (
            db.query(User)
            .filter(
                User.email == email
            )
            .one()
        )

        business = (
            db.query(Business)
            .filter(
                Business.business_uid
                == business_uid
            )
            .one()
        )

        membership = (
            db.query(
                BusinessMembership
            )
            .filter(
                BusinessMembership.business_uid
                == business_uid
            )
            .one()
        )

        assert (
            business.business_uid
            == business_uid
        )

        assert (
            membership.user_uid
            == user.user_uid
        )

        assert (
            membership.business_uid
            == business_uid
        )

        assert membership.role == "owner"
        assert membership.is_active is True

        assert (
            db.query(Business)
            .count()
            == 1
        )

        assert (
            db.query(
                BusinessMembership
            )
            .count()
            == 1
        )

    finally:
        db.close()
