from app.ai.operations_schema import OperationsReport
from app.workforce.runtime.operations import OperationsExecutive


def test_operations_executive_uses_structured_report():
    executive = OperationsExecutive()

    assert executive.name == "Operations"
    assert executive.response_model is OperationsReport


def test_operations_fallback_uses_supplied_values():
    executive = OperationsExecutive()

    output = executive.fallback_output(
        title="Review operations",
        description="Review operating capacity.",
        input_data={
            "daily_capacity": 100,
            "average_daily_volume": 80,
            "utilization_rate": 80,
            "cancellation_rate": 5,
            "locations_count": 2,
        },
        error_message="provider unavailable",
    )

    assessment = output["operational_assessment"]

    assert "Daily capacity: 100." in assessment
    assert "Average daily volume: 80." in assessment
    assert "Utilization rate: 80%." in assessment
    assert "Cancellation rate: 5%." in assessment
    assert "Locations: 2." in assessment
    assert output["ai_provider"] == "Fallback"


def test_operations_fallback_does_not_invent_values():
    executive = OperationsExecutive()

    output = executive.fallback_output(
        title="Review operations",
        description=None,
        input_data={},
        error_message="provider unavailable",
    )

    assessment = output["operational_assessment"]

    assert "No verified capacity" in assessment
    assert "%" not in assessment
    assert "99" not in assessment


def test_operations_fallback_detects_capacity_bottleneck():
    executive = OperationsExecutive()

    output = executive.fallback_output(
        title="Review capacity",
        description=None,
        input_data={
            "daily_capacity": 100,
            "average_daily_volume": 125,
        },
        error_message="provider unavailable",
    )

    assert any(
        "exceeds supplied daily capacity" in item
        for item in output["bottlenecks"]
    )

    assert any(
        "Demand above supplied capacity" in item
        for item in output["risks"]
    )


def test_operations_fallback_does_not_claim_bottleneck_without_evidence():
    executive = OperationsExecutive()

    output = executive.fallback_output(
        title="Review capacity",
        description=None,
        input_data={
            "daily_capacity": 100,
            "average_daily_volume": 80,
        },
        error_message="provider unavailable",
    )

    assert output["bottlenecks"] == [
        "No verified operational bottleneck can be concluded "
        "from the supplied data."
    ]


def test_operations_fallback_handles_decimal_values():
    executive = OperationsExecutive()

    output = executive.fallback_output(
        title="Review operations",
        description=None,
        input_data={
            "utilization_rate": 72.5,
            "cancellation_rate": 4.25,
        },
        error_message="provider unavailable",
    )

    assessment = output["operational_assessment"]

    assert "Utilization rate: 72.50%." in assessment
    assert "Cancellation rate: 4.25%." in assessment
