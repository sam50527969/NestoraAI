import asyncio

from app.services import business_search


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class FakeClient:
    def __init__(self, payload=None):
        self.payload = payload or []
        self.calls = []

    async def get(self, url, *, params):
        self.calls.append(
            {
                "url": url,
                "params": params,
            }
        )
        return FakeResponse(self.payload)


def test_nominatim_uses_requested_location_without_qatar_restriction():
    client = FakeClient()

    asyncio.run(
        business_search._search_nominatim(
            client,
            search_text="auto repair workshop",
            location="Dubai, United Arab Emirates",
            limit=5,
        )
    )

    assert len(client.calls) == 1

    params = client.calls[0]["params"]

    assert (
        params["q"]
        == "auto repair workshop Dubai, United Arab Emirates"
    )
    assert "countrycodes" not in params
    assert "Qatar" not in params["q"]


def test_nominatim_preserves_qatar_when_requested():
    client = FakeClient()

    asyncio.run(
        business_search._search_nominatim(
            client,
            search_text="dental clinic",
            location="Doha, Qatar",
            limit=5,
        )
    )

    params = client.calls[0]["params"]

    assert params["q"] == "dental clinic Doha, Qatar"
    assert "countrycodes" not in params


def test_verified_qatar_fallback_is_hidden_outside_qatar():
    matches = business_search._get_verified_matches(
        "Reem Medical Center",
        "Dubai, United Arab Emirates",
    )

    assert matches == []


def test_verified_qatar_fallback_remains_available_in_qatar():
    matches = business_search._get_verified_matches(
        "Reem Medical Center",
        "Doha, Qatar",
    )

    assert matches
    assert matches[0]["businessName"] == "Reem Medical Center"
    assert matches[0]["source"] == "verified_qatar_directory"


def test_verified_qatar_fallback_is_hidden_for_us_location():
    matches = business_search._get_verified_matches(
        "Reem Medical Center",
        "Houston, Texas, United States",
    )

    assert matches == []
