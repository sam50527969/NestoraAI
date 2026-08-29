from __future__ import annotations

from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.models import User
from app.business.models import (
    BusinessProfile,
    BusinessSize,
    BusinessTeam,
    CustomerProfile,
    FinancialProfile,
    IndustryType,
    OperationalProfile,
)
from app.database.database import Base
from app.database.models import (
    Business,
    BusinessMembership,
)
from app.services.business_onboarding_service import (
    BusinessOnboardingService,
)


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    Session = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    session = Session()

    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def make_user(
    db,
    *,
    user_uid: str = "usr-owner-test",
):
    user = User(
        user_uid=user_uid,
        email=f"{user_uid}@example.com",
        full_name="Owner Test",
        password_hash="test-hash",
        role="user",
        is_active=True,
    )

    db.add(user)
    db.commit()

    return user_uid


def make_business(
    business_uid: str = "biz-owner-test",
) -> BusinessProfile:
    return BusinessProfile(
        id=business_uid,
        name="Global Owner Test",
        industry=IndustryType.OTHER,
        country="Australia",
        city="Sydney",
        region="New South Wales",
        timezone="Australia/Sydney",
        locale="en-AU",
        size=BusinessSize.SMALL,
        description="Atomic onboarding test.",
        customers=CustomerProfile(),
        finances=FinancialProfile(
            currency="AUD",
        ),
        operations=OperationalProfile(),
        team=BusinessTeam(),
        goals=[],
        metadata={},
    )


def test_onboarding_creates_business_and_owner(
    db,
):
    user_uid = make_user(db)

    service = BusinessOnboardingService(db)

    business, membership = (
        service.create_business_for_owner(
            business=make_business(),
            owner_user_uid=user_uid,
        )
    )

    assert business is not None
    assert business.id == "biz-owner-test"

    assert membership.business_uid == business.id
    assert membership.user_uid == user_uid
    assert membership.role == "owner"
    assert membership.is_active is True

    assert (
        db.query(Business)
        .filter(
            Business.business_uid
            == business.id
        )
        .count()
        == 1
    )

    assert (
        db.query(BusinessMembership)
        .filter(
            BusinessMembership.business_uid
            == business.id
        )
        .count()
        == 1
    )


def test_membership_failure_rolls_back_business(
    db,
):
    user_uid = make_user(db)

    service = BusinessOnboardingService(db)

    with patch(
        "app.services.business_onboarding_service."
        "add_membership",
        side_effect=RuntimeError(
            "membership failure"
        ),
    ):
        with pytest.raises(
            RuntimeError,
            match="membership failure",
        ):
            service.create_business_for_owner(
                business=make_business(
                    "biz-rollback-test"
                ),
                owner_user_uid=user_uid,
            )

    assert (
        db.query(Business)
        .filter(
            Business.business_uid
            == "biz-rollback-test"
        )
        .count()
        == 0
    )

    assert (
        db.query(BusinessMembership)
        .filter(
            BusinessMembership.business_uid
            == "biz-rollback-test"
        )
        .count()
        == 0
    )


def test_invalid_owner_rolls_back_business(
    db,
):
    service = BusinessOnboardingService(db)

    with pytest.raises(
        ValueError,
        match="does not exist",
    ):
        service.create_business_for_owner(
            business=make_business(
                "biz-invalid-owner"
            ),
            owner_user_uid="usr-missing",
        )

    assert (
        db.query(Business)
        .filter(
            Business.business_uid
            == "biz-invalid-owner"
        )
        .count()
        == 0
    )
