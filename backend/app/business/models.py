from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class IndustryType(str, Enum):
    """
    Business industries initially supported by Nestora.
    """

    HEALTHCARE = "healthcare"
    DENTAL = "dental"
    BEAUTY = "beauty"
    RETAIL = "retail"
    ECOMMERCE = "ecommerce"
    PROFESSIONAL_SERVICES = "professional_services"
    HOME_SERVICES = "home_services"
    HOSPITALITY = "hospitality"
    OTHER = "other"


class BusinessSize(str, Enum):
    """
    General business-size classification.
    """

    SOLO = "solo"
    MICRO = "micro"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


@dataclass(slots=True)
class WorkingHours:
    """
    Standard working hours for one day.

    Times use 24-hour HH:MM format.
    """

    day: str
    opens_at: str | None = None
    closes_at: str | None = None
    is_closed: bool = False


@dataclass(slots=True)
class BusinessTeam:
    """
    Summary of the people and departments operating the business.
    """

    employee_count: int = 0

    departments: list[str] = field(default_factory=list)

    roles: dict[str, int] = field(default_factory=dict)


@dataclass(slots=True)
class CustomerProfile:
    """
    High-level customer information used for business reasoning.
    """

    total_customers: int = 0

    active_customers: int = 0

    inactive_customers: int = 0

    average_monthly_customers: int = 0

    returning_customer_rate: float | None = None

    average_customer_value: float | None = None


@dataclass(slots=True)
class FinancialProfile:
    """
    Financial information available to the AI CEO.
    """

    currency: str = "QAR"

    monthly_revenue: float | None = None

    monthly_expenses: float | None = None

    average_transaction_value: float | None = None

    marketing_budget: float | None = None

    outstanding_receivables: float | None = None

    @property
    def estimated_monthly_profit(self) -> float | None:
        if (
            self.monthly_revenue is None
            or self.monthly_expenses is None
        ):
            return None

        return self.monthly_revenue - self.monthly_expenses


@dataclass(slots=True)
class OperationalProfile:
    """
    Operational capacity and performance indicators.
    """

    daily_capacity: int | None = None

    average_daily_volume: int | None = None

    cancellation_rate: float | None = None

    utilization_rate: float | None = None

    locations_count: int = 1

    working_hours: list[WorkingHours] = field(
        default_factory=list,
    )


@dataclass(slots=True)
class BusinessProfile:
    """
    Nestora's structured digital representation of a business.

    This profile supplies shared context to the AI CEO,
    Objective Engine, strategists, and department executives.
    """

    id: str

    name: str

    industry: IndustryType

    country: str

    city: str | None = None

    region: str | None = None

    timezone: str | None = None

    locale: str | None = None

    size: BusinessSize = BusinessSize.SMALL

    description: str = ""

    team: BusinessTeam = field(
        default_factory=BusinessTeam,
    )

    customers: CustomerProfile = field(
        default_factory=CustomerProfile,
    )

    finances: FinancialProfile = field(
        default_factory=FinancialProfile,
    )

    operations: OperationalProfile = field(
        default_factory=OperationalProfile,
    )

    goals: list[str] = field(
        default_factory=list,
    )

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    created_at: datetime = field(
        default_factory=lambda: datetime.now(UTC),
    )

    updated_at: datetime = field(
        default_factory=lambda: datetime.now(UTC),
    )

    def validate(self) -> None:
        """
        Validate essential business profile information.
        """

        if not self.id.strip():
            raise ValueError(
                "Business ID cannot be empty."
            )

        if not self.name.strip():
            raise ValueError(
                "Business name cannot be empty."
            )

        if not self.country.strip():
            raise ValueError(
                "Business country cannot be empty."
            )

        if self.team.employee_count < 0:
            raise ValueError(
                "Employee count cannot be negative."
            )

        if self.customers.total_customers < 0:
            raise ValueError(
                "Customer count cannot be negative."
            )

        if self.operations.locations_count < 1:
            raise ValueError(
                "A business must have at least one location."
            )