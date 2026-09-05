from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.schemas.outreach import DEFAULT_OUTREACH_OFFER
from app.services.agents.outreach_agent import OutreachAgent
from app.services.agents.sales_agent import SalesAgent


def make_request(**overrides):
    values = {
        "generate_outreach": True,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


@pytest.mark.parametrize(
    ("currency", "expected"),
    [
        ("AED", "AED 12000"),
        ("QAR", "QAR 12000"),
        ("USD", "USD 12000"),
        ("aed", "AED 12000"),
    ],
)
def test_sales_agent_formats_explicit_currency(
    currency,
    expected,
):
    agent = SalesAgent(
        db=MagicMock(),
        mission_id="mission-currency",
        request=make_request(
            currency=currency,
        ),
    )

    assert (
        agent._format_estimated_value(12000)
        == expected
    )


def test_sales_agent_does_not_invent_currency():
    agent = SalesAgent(
        db=MagicMock(),
        mission_id="mission-neutral",
        request=make_request(),
    )

    assert (
        agent._format_estimated_value(12000)
        == "12000"
    )


@pytest.mark.anyio
async def test_outreach_agent_uses_neutral_default_offer():
    agent = OutreachAgent(
        db=MagicMock(),
        mission_id="mission-outreach",
        request=make_request(),
    )

    agent.task_progress = MagicMock()
    agent.update_status = MagicMock()
    agent.update_mission = MagicMock()
    agent.log = MagicMock()

    lead = {
        "businessName": "Atlas Auto Care",
        "category": "auto repair",
        "phone": "+971500000000",
        "website": "https://atlas.example",
        "priority": "High",
    }

    analysis = {
        "recommendation": (
            "Offer a digital visibility audit."
        ),
    }

    with patch(
        "app.services.agents.outreach_agent.generate_outreach"
    ) as generate_mock:
        generate_mock.return_value = MagicMock()

        await agent.run(
            lead=lead,
            analysis=analysis,
            index=1,
            total=1,
        )

    request = generate_mock.call_args.args[0]

    assert request.offer == DEFAULT_OUTREACH_OFFER
    assert request.offer == "starter business package"
    assert "QAR" not in request.offer
    assert "AED" not in request.offer
    assert "USD" not in request.offer
    assert "99" not in request.offer
