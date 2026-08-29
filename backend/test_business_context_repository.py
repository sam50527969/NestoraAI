from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.business.models import (
    BusinessProfile,
    FinancialProfile,
    IndustryType,
)
from app.database.models import Base
from app.repositories.business_repository import BusinessRepository


def make_repository() -> BusinessRepository:
    engine = create_engine(
        "sqlite://",
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    session_factory = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    return BusinessRepository(
        session_factory()
    )


def test_repository_resolves_business_context():
    repository = make_repository()

    repository.create(
        BusinessProfile(
            id="biz-context-repository-test",
            name="Sydney Advisory",
            industry=IndustryType.PROFESSIONAL_SERVICES,
            country="Australia",
            city="Sydney",
            region="New South Wales",
            timezone="Australia/Sydney",
            locale="en-AU",
            finances=FinancialProfile(
                currency="AUD",
            ),
        )
    )

    context = repository.get_context(
        "biz-context-repository-test"
    )

    assert context is not None
    assert context.business_id == "biz-context-repository-test"
    assert context.business_name == "Sydney Advisory"
    assert context.country == "Australia"
    assert context.city == "Sydney"
    assert context.region == "New South Wales"
    assert context.timezone == "Australia/Sydney"
    assert context.locale == "en-AU"
    assert context.currency == "AUD"
    assert (
        context.location
        == "Sydney, New South Wales, Australia"
    )


def test_repository_context_returns_none_for_unknown_business():
    repository = make_repository()

    context = repository.get_context(
        "biz-does-not-exist"
    )

    assert context is None
