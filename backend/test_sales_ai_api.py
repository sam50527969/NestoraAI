import warnings

import pytest
from fastapi import FastAPI

with warnings.catch_warnings():
    warnings.simplefilter("ignore")

    from fastapi.testclient import (
        TestClient,
    )

from app.routes.sales_ai import (
    router as sales_ai_router,
)


@pytest.fixture()
def sales_ai_api():
    app = FastAPI()

    app.include_router(
        sales_ai_router
    )

    with TestClient(app) as client:
        yield client


def analyze(
    client: TestClient,
    lead: dict,
):
    return client.post(
        "/sales-ai/analyze",
        json={
            "lead": lead,
        },
    )


def test_high_value_lead_scores_100(
    sales_ai_api,
):
    response = analyze(
        sales_ai_api,
        {
            "name": (
                "Gulf Neon Advertising"
            ),
            "category": "clinic",
            "phone": "+974 5555 0000",
            "website": (
                "https://example.com"
            ),
            "priority": "High",
            "notes": (
                "Requested a digital "
                "growth proposal."
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["score"] == 100

    assert len(data["strengths"]) == 5
    assert data["weaknesses"] == []

    assert (
        "Contact immediately"
        in data["recommendation"]
    )

    assert (
        "enough contact information"
        in data["opportunity"]
    )


def test_missing_contact_details_are_scored(
    sales_ai_api,
):
    response = analyze(
        sales_ai_api,
        {
            "name": "Minimal Clinic",
            "category": "clinic",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["score"] == 60

    assert (
        "No usable phone number found"
        in data["weaknesses"]
    )

    assert any(
        "No website found"
        in weakness
        for weakness in data[
            "weaknesses"
        ]
    )

    assert (
        "website or digital presence"
        in data["opportunity"]
    )


def test_website_without_phone_branch(
    sales_ai_api,
):
    response = analyze(
        sales_ai_api,
        {
            "name": (
                "Website Only Business"
            ),
            "website": (
                "https://example.com"
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["score"] == 50

    assert (
        "website but limited contact"
        in data["opportunity"]
    )

    assert (
        "Enrich the lead"
        in data["recommendation"]
    )


def test_low_priority_reduces_score(
    sales_ai_api,
):
    response = analyze(
        sales_ai_api,
        {
            "name": "Low Priority Lead",
            "phone": "+974 5555 1111",
            "website": (
                "https://example.com"
            ),
            "priority": "Low",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["score"] == 65

    assert (
        "Lead is currently marked "
        "as low priority"
        in data["weaknesses"]
    )


@pytest.mark.parametrize(
    "empty_value",
    [
        "Not found",
        "not found",
        "UNKNOWN",
        "N/A",
        " none ",
        "null",
    ],
)
def test_placeholder_contact_values_are_missing(
    sales_ai_api,
    empty_value,
):
    response = analyze(
        sales_ai_api,
        {
            "name": "Placeholder Lead",
            "phone": empty_value,
            "website": empty_value,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["score"] == 45

    assert (
        "No usable phone number found"
        in data["weaknesses"]
    )

    assert any(
        "No website found"
        in weakness
        for weakness in data[
            "weaknesses"
        ]
    )


def test_normalizes_lead_name(
    sales_ai_api,
):
    response = analyze(
        sales_ai_api,
        {
            "name": (
                "  Gulf   Neon  "
            ),
        },
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {
            "lead": {},
        },
        {
            "lead": {
                "name": "",
            },
        },
        {
            "lead": {
                "name": "   ",
            },
        },
        {
            "lead": {
                "name": "A" * 241,
            },
        },
    ],
)
def test_rejects_invalid_payload(
    sales_ai_api,
    payload,
):
    response = sales_ai_api.post(
        "/sales-ai/analyze",
        json=payload,
    )

    assert response.status_code == 422


def test_optional_fields_are_optional(
    sales_ai_api,
):
    response = analyze(
        sales_ai_api,
        {
            "name": "Basic Lead",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["score"] == 45

    assert isinstance(
        data["strengths"],
        list,
    )

    assert isinstance(
        data["weaknesses"],
        list,
    )

    assert data["recommendation"]
    assert data["opportunity"]