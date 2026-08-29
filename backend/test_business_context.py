from __future__ import annotations

from app.business.context import BusinessContext
from app.business.models import (
    BusinessProfile,
    FinancialProfile,
    IndustryType,
)


def make_business(
    *,
    country: str,
    city: str | None,
    region: str | None,
    timezone: str | None,
    locale: str | None,
    currency: str,
) -> BusinessProfile:
    return BusinessProfile(
        id="biz-global-context-test",
        name="Global Context Test",
        industry=IndustryType.PROFESSIONAL_SERVICES,
        country=country,
        city=city,
        region=region,
        timezone=timezone,
        locale=locale,
        finances=FinancialProfile(
            currency=currency,
        ),
    )


def test_business_context_resolves_global_profile():
    business = make_business(
        country="United Kingdom",
        city="London",
        region="England",
        timezone="Europe/London",
        locale="en-GB",
        currency="gbp",
    )

    context = BusinessContext.from_business(business)

    assert context.business_id == "biz-global-context-test"
    assert context.business_name == "Global Context Test"
    assert context.country == "United Kingdom"
    assert context.city == "London"
    assert context.region == "England"
    assert context.timezone == "Europe/London"
    assert context.locale == "en-GB"
    assert context.currency == "GBP"
    assert context.location == "London, England, United Kingdom"


def test_business_context_supports_minimal_location():
    business = make_business(
        country="Australia",
        city=None,
        region=None,
        timezone=None,
        locale=None,
        currency="AUD",
    )

    context = BusinessContext.from_business(business)

    assert context.location == "Australia"
    assert context.city is None
    assert context.region is None
    assert context.timezone is None
    assert context.locale is None
    assert context.currency == "AUD"


def test_business_context_removes_duplicate_location_parts():
    business = make_business(
        country="Singapore",
        city="Singapore",
        region=None,
        timezone="Asia/Singapore",
        locale="en-SG",
        currency="SGD",
    )

    context = BusinessContext.from_business(business)

    assert context.location == "Singapore"


def test_business_context_normalizes_optional_values():
    business = make_business(
        country="Canada",
        city=" Toronto ",
        region=" Ontario ",
        timezone=" America/Toronto ",
        locale=" en-CA ",
        currency=" cad ",
    )

    context = BusinessContext.from_business(business)

    assert context.city == "Toronto"
    assert context.region == "Ontario"
    assert context.timezone == "America/Toronto"
    assert context.locale == "en-CA"
    assert context.currency == "CAD"
    assert context.location == "Toronto, Ontario, Canada"
