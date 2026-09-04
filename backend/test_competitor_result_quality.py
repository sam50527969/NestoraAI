from app.services.competitor_enrichment.phone_discovery import (
    _extract_phone_from_text,
    _normalize_phone,
)
from app.services.competitor_filter import (
    CompetitorFilterService,
)
from app.services.google_places import _build_result


def test_auto_repair_filter_accepts_relevant_google_business():
    service = CompetitorFilterService()

    result = service.evaluate(
        competitor={
            "businessName": "Dubai Auto Care Garage",
            "category": "car repair",
            "location": "Al Quoz, Dubai, United Arab Emirates",
        },
        target_industry="Auto Repair Workshop",
        target_location="Dubai, United Arab Emirates",
    )

    assert result.included is True
    assert result.score >= 35


def test_auto_repair_filter_rejects_country_entity():
    service = CompetitorFilterService()

    result = service.evaluate(
        competitor={
            "businessName": "United Arab Emirates",
            "category": "country",
            "location": "United Arab Emirates",
        },
        target_industry="Auto Repair Workshop",
        target_location="Dubai, United Arab Emirates",
    )

    assert result.included is False


def test_google_result_does_not_invent_doha_location():
    result = _build_result(
        place={
            "id": "example-place",
            "displayName": {
                "text": "Atlas Competitor Garage",
            },
            "primaryType": "car_repair",
        },
        business_type="car repair",
        index=1,
    )

    assert result["location"] == "Not found"
    assert "Doha" not in result["location"]
    assert "Qatar" not in result["location"]


def test_phone_normalization_preserves_international_country_code():
    assert (
        _normalize_phone("+971 4 123 4567")
        == "+97141234567"
    )

    assert (
        _normalize_phone("00971 4 123 4567")
        == "+97141234567"
    )


def test_phone_normalization_does_not_invent_qatar_code():
    assert _normalize_phone("44123456") == "44123456"

    assert (
        _extract_phone_from_text(
            "Call us on 44123456 for assistance."
        )
        is None
    )

    assert (
        _extract_phone_from_text(
            "Call us on +971 4 123 4567."
        )
        == "+97141234567"
    )
