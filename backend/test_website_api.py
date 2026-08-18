import warnings

import pytest
from fastapi import FastAPI

with warnings.catch_warnings():
    warnings.simplefilter("ignore")

    from fastapi.testclient import (
        TestClient,
    )

from app.routes.website import (
    router as website_router,
)
from app.services.website_intelligence import (
    WebsiteIntelligenceService,
)


@pytest.fixture()
def website_api():
    app = FastAPI()

    app.include_router(
        website_router
    )

    with TestClient(app) as client:
        yield client


def test_analyze_secure_website(
    website_api,
):
    response = website_api.post(
        "/website/analyze",
        json={
            "url": (
                "https://www.example.com"
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["score"] == 75

    assert (
        "Secure HTTPS connection"
        in data["strengths"]
    )

    assert (
        "Standard domain format"
        in data["strengths"]
    )

    assert (
        "Clean URL structure"
        in data["strengths"]
    )

    assert len(data["issues"]) == 3


def test_analyze_http_website(
    website_api,
):
    response = website_api.post(
        "/website/analyze",
        json={
            "url": "http://example.com",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["score"] == 55

    assert (
        "Website is not using HTTPS"
        in data["issues"]
    )


def test_bare_domain_is_normalized(
    website_api,
):
    response = website_api.post(
        "/website/analyze",
        json={
            "url": "example.com",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["score"] == 70

    assert (
        "Secure HTTPS connection"
        in data["strengths"]
    )


@pytest.mark.parametrize(
    "url",
    [
        "",
        "   ",
        "ftp://example.com",
        "http://localhost",
        "http://localhost:8000",
        "http://127.0.0.1",
        "http://10.0.0.10",
        "http://172.16.0.10",
        "http://192.168.1.10",
        "http://169.254.169.254",
        "http://[::1]",
        "http://user:password@example.com",
    ],
)
def test_rejects_unsafe_url(
    website_api,
    url,
):
    response = website_api.post(
        "/website/analyze",
        json={
            "url": url,
        },
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {
            "url": None,
        },
        {
            "url": 123,
        },
        {
            "url": [],
        },
    ],
)
def test_rejects_invalid_payload(
    website_api,
    payload,
):
    response = website_api.post(
        "/website/analyze",
        json=payload,
    )

    assert response.status_code == 422


def test_intelligence_returns_profile(
    website_api,
    monkeypatch,
):
    class FakeProfile:
        def to_dict(self):
            return {
                "website": (
                    "https://example.com"
                ),
                "status": "completed",
                "confidence": 80,
            }

    async def fake_analyze(
        self,
        *,
        website,
        business_name=None,
    ):
        assert website == (
            "https://example.com"
        )
        assert business_name is None

        return FakeProfile()

    monkeypatch.setattr(
        WebsiteIntelligenceService,
        "analyze",
        fake_analyze,
    )

    response = website_api.post(
        "/website/intelligence",
        json={
            "url": "example.com",
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "website": "https://example.com",
        "status": "completed",
        "confidence": 80,
    }


def test_intelligence_failure_is_safe(
    website_api,
    monkeypatch,
):
    async def failing_analyze(
        self,
        *,
        website,
        business_name=None,
    ):
        raise RuntimeError(
            "Sensitive internal provider error"
        )

    monkeypatch.setattr(
        WebsiteIntelligenceService,
        "analyze",
        failing_analyze,
    )

    response = website_api.post(
        "/website/intelligence",
        json={
            "url": "https://example.com",
        },
    )

    assert response.status_code == 502

    assert response.json() == {
        "detail": (
            "Website intelligence analysis "
            "could not be completed."
        ),
    }

    assert (
        "Sensitive internal provider error"
        not in response.text
    )