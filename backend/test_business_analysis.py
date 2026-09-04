import pytest
from pydantic import ValidationError

from app.routes.business_analysis import (
    BusinessAnalysisRequest,
)


def test_business_analysis_defaults_are_business_neutral():
    request = BusinessAnalysisRequest(
        business_name="Atlas Auto Care",
        industry="Auto Repair Workshop",
        location="Dubai, United Arab Emirates",
        currency="AED",
    )

    assert request.location == "Dubai, United Arab Emirates"
    assert request.currency == "AED"
    assert request.objective == "Increase qualified leads and revenue"
    assert request.timeline_days == 90
    assert request.monthly_budget == 0.0
    assert request.average_sale_value == 500.0
    assert request.competitor_limit == 5


@pytest.mark.parametrize(
    "missing_field",
    ["location", "currency"],
)
def test_business_analysis_requires_workspace_context(
    missing_field,
):
    payload = {
        "business_name": "Atlas Auto Care",
        "industry": "Auto Repair Workshop",
        "location": "Dubai, United Arab Emirates",
        "currency": "AED",
    }
    payload.pop(missing_field)

    with pytest.raises(ValidationError):
        BusinessAnalysisRequest(**payload)
