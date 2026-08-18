import warnings

import pytest
from fastapi import FastAPI

with warnings.catch_warnings():
    warnings.simplefilter("ignore")

    from fastapi.testclient import (
        TestClient,
    )

from app.routes.outreach import (
    router as outreach_router,
)


@pytest.fixture()
def outreach_generation_api():
    app = FastAPI()

    app.include_router(
        outreach_router
    )

    with TestClient(app) as client:
        yield client


def test_generates_personalized_outreach(
    outreach_generation_api,
):
    response = (
        outreach_generation_api.post(
            "/outreach/generate",
            json={
                "lead": {
                    "name": (
                        "Gulf Neon "
                        "Advertising"
                    ),
                    "category": (
                        "advertising"
                    ),
                    "phone": (
                        "+974 5555 0000"
                    ),
                    "website": (
                        "https://"
                        "gulfneon.example"
                    ),
                    "priority": "High",
                    "notes": (
                        "Interested in "
                        "digital growth."
                    ),
                },
                "offer": (
                    "99 QAR starter "
                    "business package"
                ),
            },
        )
    )

    assert response.status_code == 200

    data = response.json()

    expected_fields = {
        "email_subject",
        "email_body",
        "whatsapp_message",
        "cold_call_script",
        "proposal_summary",
    }

    assert set(data) == expected_fields

    for value in data.values():
        assert isinstance(value, str)
        assert value.strip()

    assert (
        "Gulf Neon Advertising"
        in data["email_subject"]
    )

    assert (
        "Gulf Neon Advertising"
        in data["email_body"]
    )

    assert (
        "99 QAR starter business package"
        in data["email_body"]
    )

    assert (
        "advertising"
        in data["cold_call_script"]
    )


def test_normalizes_lead_name_and_offer(
    outreach_generation_api,
):
    response = (
        outreach_generation_api.post(
            "/outreach/generate",
            json={
                "lead": {
                    "name": (
                        "  Gulf   Neon  "
                    ),
                },
                "offer": (
                    "  growth   package  "
                ),
            },
        )
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        "Gulf Neon"
        in data["email_subject"]
    )

    assert (
        "Gulf   Neon"
        not in data["email_subject"]
    )

    assert (
        "growth package"
        in data["email_body"]
    )


def test_uses_default_offer_when_omitted(
    outreach_generation_api,
):
    response = (
        outreach_generation_api.post(
            "/outreach/generate",
            json={
                "lead": {
                    "name": (
                        "Doha Coffee House"
                    ),
                    "category": "Cafe",
                },
            },
        )
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        "starter business package"
        in data["email_body"]
    )

    assert (
        "Doha Coffee House"
        in data["whatsapp_message"]
    )


@pytest.mark.parametrize(
    "offer",
    [
        None,
        "",
        "   ",
    ],
)
def test_empty_offer_uses_default(
    outreach_generation_api,
    offer,
):
    response = (
        outreach_generation_api.post(
            "/outreach/generate",
            json={
                "lead": {
                    "name": (
                        "Test Business"
                    ),
                },
                "offer": offer,
            },
        )
    )

    assert response.status_code == 200

    assert (
        "starter business package"
        in response.json()["email_body"]
    )


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
        {
            "lead": {
                "name": "Valid Business",
            },
            "offer": "A" * 241,
        },
    ],
)
def test_rejects_invalid_payload(
    outreach_generation_api,
    payload,
):
    response = (
        outreach_generation_api.post(
            "/outreach/generate",
            json=payload,
        )
    )

    assert response.status_code == 422


def test_optional_lead_fields_are_optional(
    outreach_generation_api,
):
    response = (
        outreach_generation_api.post(
            "/outreach/generate",
            json={
                "lead": {
                    "name": (
                        "Minimal Business"
                    ),
                },
            },
        )
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        "Minimal Business"
        in data["email_body"]
    )

    assert (
        "business"
        in data["email_body"]
    )

    assert (
        "medium priority"
        in data["email_body"]
    )