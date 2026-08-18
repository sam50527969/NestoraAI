import warnings

import pytest
from fastapi import FastAPI

with warnings.catch_warnings():
    warnings.simplefilter("ignore")

    from fastapi.testclient import (
        TestClient,
    )

from app.routes import (
    search as search_routes,
)


@pytest.fixture()
def search_api():
    app = FastAPI()

    app.include_router(
        search_routes.router
    )

    with TestClient(app) as client:
        yield client


def create_search_result(
    *,
    result_id: int = 1,
    business_name: str = (
        "Gulf Neon Advertising"
    ),
) -> dict:
    return {
        "id": result_id,
        "businessName": business_name,
        "category": "advertising",
        "location": "Doha, Qatar",
        "phone": "+974 5555 0000",
        "email": "info@example.com",
        "website": (
            "https://example.com"
        ),
        "latitude": 25.2854,
        "longitude": 51.5310,
        "source": "Google Places",
        "status": "New",
        "opportunityScore": 90,
        "contactQuality": 90,
        "nameMatchScore": 100,
        "rankingScore": 97,
        "websiteAvailable": True,
        "phoneAvailable": True,
        "priority": "High",
        "aiRecommendation": (
            "High-priority lead."
        ),
    }


def test_business_search_returns_results(
    search_api,
    monkeypatch,
):
    received_arguments = {}

    async def fake_search_businesses(
        business_type,
        location,
        limit,
    ):
        received_arguments.update(
            {
                "business_type": (
                    business_type
                ),
                "location": location,
                "limit": limit,
            }
        )

        return [
            create_search_result()
        ]

    monkeypatch.setattr(
        search_routes,
        "search_businesses",
        fake_search_businesses,
    )

    response = search_api.get(
        "/search/businesses",
        params={
            "business_type": (
                "  Gulf   Neon  "
            ),
            "location": (
                "  Doha,   Qatar  "
            ),
            "limit": 10,
        },
    )

    assert response.status_code == 200

    results = response.json()

    assert len(results) == 1

    assert (
        results[0]["businessName"]
        == "Gulf Neon Advertising"
    )

    assert received_arguments == {
        "business_type": "Gulf Neon",
        "location": "Doha, Qatar",
        "limit": 10,
    }


def test_business_search_uses_default_limit(
    search_api,
    monkeypatch,
):
    received_limit = None

    async def fake_search_businesses(
        business_type,
        location,
        limit,
    ):
        nonlocal received_limit

        received_limit = limit

        return []

    monkeypatch.setattr(
        search_routes,
        "search_businesses",
        fake_search_businesses,
    )

    response = search_api.get(
        "/search/businesses",
        params={
            "business_type": "clinic",
            "location": "Doha",
        },
    )

    assert response.status_code == 200
    assert response.json() == []
    assert received_limit == 20


def test_business_search_can_return_empty_list(
    search_api,
    monkeypatch,
):
    async def fake_search_businesses(
        business_type,
        location,
        limit,
    ):
        return []

    monkeypatch.setattr(
        search_routes,
        "search_businesses",
        fake_search_businesses,
    )

    response = search_api.get(
        "/search/businesses",
        params={
            "business_type": (
                "Unlisted business"
            ),
            "location": "Doha",
            "limit": 5,
        },
    )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize(
    "params",
    [
        {
            "location": "Doha",
        },
        {
            "business_type": "clinic",
        },
        {
            "business_type": "clinic",
            "location": "Doha",
            "limit": 0,
        },
        {
            "business_type": "clinic",
            "location": "Doha",
            "limit": 101,
        },
    ],
)
def test_business_search_rejects_invalid_query(
    search_api,
    params,
):
    response = search_api.get(
        "/search/businesses",
        params=params,
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    (
        "business_type",
        "location",
        "expected_detail",
    ),
    [
        (
            "   ",
            "Doha",
            (
                "Business type must not "
                "be empty."
            ),
        ),
        (
            "clinic",
            "   ",
            (
                "Location must not be empty."
            ),
        ),
    ],
)
def test_business_search_rejects_whitespace(
    search_api,
    business_type,
    location,
    expected_detail,
):
    response = search_api.get(
        "/search/businesses",
        params={
            "business_type": business_type,
            "location": location,
        },
    )

    assert response.status_code == 422

    assert response.json() == {
        "detail": expected_detail,
    }


def test_provider_failure_returns_503(
    search_api,
    monkeypatch,
):
    async def fake_search_businesses(
        business_type,
        location,
        limit,
    ):
        raise RuntimeError(
            "All providers failed."
        )

    monkeypatch.setattr(
        search_routes,
        "search_businesses",
        fake_search_businesses,
    )

    response = search_api.get(
        "/search/businesses",
        params={
            "business_type": "clinic",
            "location": "Doha",
        },
    )

    assert response.status_code == 503

    assert response.json() == {
        "detail": (
            "Business search providers "
            "are temporarily unavailable."
        )
    }