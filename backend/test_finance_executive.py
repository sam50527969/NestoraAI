import pytest

from app.ai.finance_schema import FinanceReport
from app.workforce.runtime.finance import FinanceExecutive


def test_finance_executive_uses_structured_report():
    executive = FinanceExecutive()

    assert executive.name == "Finance"
    assert executive.response_model is FinanceReport


@pytest.mark.parametrize(
    ("currency", "expected"),
    [
        ("AED", "AED 25,000.00"),
        ("QAR", "QAR 25,000.00"),
        ("USD", "USD 25,000.00"),
    ],
)
def test_finance_fallback_uses_supplied_currency(
    currency,
    expected,
):
    executive = FinanceExecutive()

    output = executive.fallback_output(
        title="Review financial performance",
        description="Review current business finances.",
        input_data={
            "currency": currency,
            "monthly_revenue": 100000,
            "monthly_expenses": 75000,
        },
        error_message="provider unavailable",
    )

    assert expected in output["financial_assessment"]
    assert output["ai_provider"] == "Fallback"


def test_finance_fallback_calculates_profit_from_supplied_values():
    executive = FinanceExecutive()

    output = executive.fallback_output(
        title="Review profitability",
        description=None,
        input_data={
            "currency": "USD",
            "monthly_revenue": 100000,
            "monthly_expenses": 75000,
        },
        error_message="provider unavailable",
    )

    assert (
        "Estimated monthly profit: USD 25,000.00."
        in output["financial_assessment"]
    )


def test_finance_fallback_does_not_invent_currency():
    executive = FinanceExecutive()

    output = executive.fallback_output(
        title="Review profitability",
        description=None,
        input_data={
            "monthly_revenue": 100000,
            "monthly_expenses": 75000,
        },
        error_message="provider unavailable",
    )

    assessment = output["financial_assessment"]

    assert "25,000.00" in assessment
    assert "QAR" not in assessment
    assert "AED" not in assessment
    assert "USD" not in assessment


def test_finance_fallback_does_not_invent_financial_values():
    executive = FinanceExecutive()

    output = executive.fallback_output(
        title="Review finances",
        description=None,
        input_data={},
        error_message="provider unavailable",
    )

    assessment = output["financial_assessment"]

    assert "No verified revenue" in assessment
    assert "99" not in assessment
    assert "QAR" not in assessment
    assert "AED" not in assessment
    assert "USD" not in assessment


def test_finance_fallback_flags_negative_profit():
    executive = FinanceExecutive()

    output = executive.fallback_output(
        title="Review financial risk",
        description=None,
        input_data={
            "currency": "QAR",
            "monthly_revenue": 50000,
            "monthly_expenses": 70000,
        },
        error_message="provider unavailable",
    )

    assert any(
        "negative monthly profitability" in risk
        for risk in output["risks"]
    )
