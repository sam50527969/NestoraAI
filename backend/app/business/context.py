from __future__ import annotations

from dataclasses import dataclass

from app.business.models import BusinessProfile


@dataclass(frozen=True, slots=True)
class BusinessContext:
    """
    Canonical location and localization context for a business.

    This object is intentionally independent of any specific
    country, industry, executive, or external provider.
    """

    business_id: str
    business_name: str
    industry: str
    country: str
    city: str | None
    region: str | None
    timezone: str | None
    locale: str | None
    currency: str

    @property
    def location(self) -> str:
        """
        Build the most useful human-readable location available.
        """

        parts: list[str] = []

        for value in (
            self.city,
            self.region,
            self.country,
        ):
            cleaned = str(value or "").strip()

            if cleaned and cleaned not in parts:
                parts.append(cleaned)

        return ", ".join(parts)

    @classmethod
    def from_business(
        cls,
        business: BusinessProfile,
    ) -> "BusinessContext":
        """
        Resolve canonical execution context from a BusinessProfile.
        """

        business.validate()

        return cls(
            business_id=business.id.strip(),
            business_name=business.name.strip(),
            industry=business.industry.value,
            country=business.country.strip(),
            city=_clean_optional(business.city),
            region=_clean_optional(business.region),
            timezone=_clean_optional(business.timezone),
            locale=_clean_optional(business.locale),
            currency=_normalize_currency(
                business.finances.currency
            ),
        )


def _clean_optional(
    value: str | None,
) -> str | None:
    cleaned = str(value or "").strip()

    return cleaned or None


def _normalize_currency(
    value: str,
) -> str:
    cleaned = str(value or "").strip().upper()

    if not cleaned:
        raise ValueError(
            "Business currency must not be empty."
        )

    return cleaned
