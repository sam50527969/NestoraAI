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
from app.schemas.business import BusinessCreateRequest


def make_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    session_factory = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    return session_factory()


def test_business_profile_accepts_global_context():
    business = BusinessProfile(
        id="biz_global_profile",
        name="Global Business",
        industry=IndustryType.PROFESSIONAL_SERVICES,
        country="United Kingdom",
        city="London",
        region="England",
        timezone="Europe/London",
        locale="en-GB",
        finances=FinancialProfile(
            currency="GBP",
        ),
    )

    business.validate()

    assert business.country == "United Kingdom"
    assert business.city == "London"
    assert business.region == "England"
    assert business.timezone == "Europe/London"
    assert business.locale == "en-GB"
    assert business.finances.currency == "GBP"


def test_business_profile_keeps_new_context_optional():
    business = BusinessProfile(
        id="biz_legacy_profile",
        name="Legacy Business",
        industry=IndustryType.OTHER,
        country="Qatar",
    )

    business.validate()

    assert business.city is None
    assert business.region is None
    assert business.timezone is None
    assert business.locale is None


def test_business_create_schema_accepts_global_context():
    request = BusinessCreateRequest(
        name="European Business",
        industry=IndustryType.RETAIL,
        country="Germany",
        city="Berlin",
        region="Berlin",
        timezone="Europe/Berlin",
        locale="de-DE",
    )

    assert request.country == "Germany"
    assert request.city == "Berlin"
    assert request.region == "Berlin"
    assert request.timezone == "Europe/Berlin"
    assert request.locale == "de-DE"


def test_repository_round_trips_global_context():
    db = make_session()

    try:
        repository = BusinessRepository(db)

        business = BusinessProfile(
            id="biz_repository_global",
            name="Australian Business",
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

        created = repository.create(business)

        assert created.city == "Sydney"
        assert created.region == "New South Wales"
        assert created.timezone == "Australia/Sydney"
        assert created.locale == "en-AU"

        loaded = repository.get_by_uid(
            "biz_repository_global"
        )

        assert loaded is not None
        assert loaded.country == "Australia"
        assert loaded.city == "Sydney"
        assert loaded.region == "New South Wales"
        assert loaded.timezone == "Australia/Sydney"
        assert loaded.locale == "en-AU"
        assert loaded.finances.currency == "AUD"

    finally:
        db.close()


def test_repository_normalizes_optional_context():
    db = make_session()

    try:
        repository = BusinessRepository(db)

        business = BusinessProfile(
            id="biz_context_normalization",
            name="Normalization Business",
            industry=IndustryType.OTHER,
            country="Canada",
            city="  Toronto  ",
            region="  Ontario  ",
            timezone="  America/Toronto  ",
            locale="  en-CA  ",
        )

        repository.create(business)

        loaded = repository.get_by_uid(
            "biz_context_normalization"
        )

        assert loaded is not None
        assert loaded.city == "Toronto"
        assert loaded.region == "Ontario"
        assert loaded.timezone == "America/Toronto"
        assert loaded.locale == "en-CA"

    finally:
        db.close()


def test_repository_converts_blank_context_to_none():
    db = make_session()

    try:
        repository = BusinessRepository(db)

        business = BusinessProfile(
            id="biz_blank_context",
            name="Blank Context Business",
            industry=IndustryType.OTHER,
            country="Singapore",
            city="   ",
            region="",
            timezone=None,
            locale="   ",
        )

        repository.create(business)

        loaded = repository.get_by_uid(
            "biz_blank_context"
        )

        assert loaded is not None
        assert loaded.city is None
        assert loaded.region is None
        assert loaded.timezone is None
        assert loaded.locale is None

    finally:
        db.close()
