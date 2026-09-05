from types import SimpleNamespace
from unittest.mock import Mock

import pytest

import app.services.mission_executor as mission_executor_module
from app.services.mission_executor import MissionExecutor


@pytest.mark.parametrize(
    "currency",
    ["AED", "QAR", "USD"],
)
def test_mission_executor_outreach_does_not_invent_price(
    monkeypatch,
    currency,
):
    captured = {}

    def fake_generate_outreach(request):
        captured["request"] = request
        return Mock()

    monkeypatch.setattr(
        mission_executor_module,
        "generate_outreach",
        fake_generate_outreach,
    )

    for function_name in (
        "start_mission_task",
        "update_mission_task_progress",
        "update_mission",
        "update_agent",
    ):
        monkeypatch.setattr(
            mission_executor_module,
            function_name,
            lambda *args, **kwargs: None,
        )

    request = SimpleNamespace(
        generate_outreach=True,
    )

    executor = MissionExecutor(
        db=object(),
        mission_id="mission-offer-neutrality",
        request=request,
        business_uid="biz-offer-neutrality",
        business_context=SimpleNamespace(
            currency=currency,
        ),
    )

    executor.accepted_count = 1
    executor.outreach_count = 0
    executor.log = Mock()

    lead = {
        "category": "business",
        "phone": None,
        "website": None,
        "priority": "Medium",
    }

    analysis = {
        "recommendation": "Potential opportunity.",
    }

    executor.generate_lead_outreach(
        lead=lead,
        business_name="Example Business",
        analysis=analysis,
        item_progress=75,
    )

    outreach_request = captured["request"]

    assert outreach_request.offer == "starter business package"
    assert "99" not in outreach_request.offer
    assert currency not in outreach_request.offer
    assert executor.outreach_count == 1
