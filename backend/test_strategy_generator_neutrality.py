from app.services.strategy_generator import (
    StrategyGeneratorService,
)


def test_strategy_uses_supplied_workspace_context():
    report = StrategyGeneratorService().generate(
        business_name="Atlas Auto Care",
        industry="Auto Repair Workshop",
        location="Dubai, United Arab Emirates",
        objective="Increase qualified leads and revenue",
        monthly_budget=5000.0,
        currency="AED",
        average_sale_value=750.0,
    )

    assert report.budget.currency == "AED"
    assert report.roi_forecast is not None
    assert report.roi_forecast.currency == "AED"

    payload = str(report.to_dict())

    assert "Dubai, United Arab Emirates" in payload
    assert "AED" in payload
    assert "Doha" not in payload
    assert "Qatar" not in payload
    assert "QAR" not in payload


def test_strategy_keywords_use_supplied_location():
    report = StrategyGeneratorService().generate(
        business_name="Atlas Auto Care",
        industry="Auto Repair Workshop",
        location="Dubai",
        objective="Increase qualified leads and revenue",
        monthly_budget=5000.0,
        currency="AED",
        average_sale_value=750.0,
    )

    seo_keywords = [
        keyword
        for action in report.seo_plan.actions
        for keyword in action.target_keywords
    ]

    ad_keywords = [
        keyword
        for campaign in report.ad_campaigns
        for keyword in campaign.keywords
    ]

    assert any("Dubai" in keyword for keyword in seo_keywords)
    assert any("Dubai" in keyword for keyword in ad_keywords)

    assert all("Qatar" not in keyword for keyword in seo_keywords)
    assert all("Qatar" not in keyword for keyword in ad_keywords)
