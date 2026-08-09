from __future__ import annotations

from typing import Any


INDUSTRY_RULES: dict[str, dict[str, Any]] = {
    "medical center": {
        "aliases": [
            "medical centre",
            "clinic",
            "healthcare",
            "health center",
            "health centre",
        ],
        "allowed_categories": [
            "hospital",
            "clinic",
            "doctors",
            "doctor",
            "dentist",
            "dental clinic",
            "physiotherapist",
            "physiotherapy",
            "dermatologist",
            "dermatology",
            "pediatrics",
            "pediatrician",
            "radiology",
            "laboratory",
            "medical laboratory",
            "healthcare",
            "medical center",
            "medical centre",
        ],
        "positive_terms": [
            "medical",
            "clinic",
            "hospital",
            "doctor",
            "doctors",
            "health",
            "dental",
            "dentist",
            "physio",
            "physiotherapy",
            "dermatology",
            "pediatric",
            "radiology",
            "laboratory",
        ],
        "excluded_categories": [
            "veterinary",
            "tailor",
            "restaurant",
            "cafe",
            "fast_food",
            "beauty",
            "salon",
            "laundry",
            "supermarket",
            "grocery",
            "car_repair",
            "pet",
        ],
        "excluded_terms": [
            "veterinary",
            "vet",
            "pet",
            "pets",
            "handbag",
            "tailor",
            "laundry",
            "restaurant",
            "cafe",
            "coffee",
            "beauty",
            "salon",
            "grocery",
            "supermarket",
            "car repair",
        ],
    },

    "dental clinic": {
        "aliases": [
            "dentist",
            "dental center",
            "dental centre",
        ],
        "allowed_categories": [
            "dentist",
            "dental clinic",
            "clinic",
            "medical center",
            "medical centre",
        ],
        "positive_terms": [
            "dental",
            "dentist",
            "orthodontic",
            "orthodontist",
            "teeth",
            "oral",
        ],
        "excluded_categories": [
            "veterinary",
            "tailor",
            "restaurant",
            "cafe",
            "beauty",
            "salon",
            "pet",
        ],
        "excluded_terms": [
            "veterinary",
            "vet",
            "pet",
            "handbag",
            "tailor",
            "restaurant",
            "cafe",
            "beauty salon",
        ],
    },

    "restaurant": {
        "aliases": [
            "food",
            "dining",
        ],
        "allowed_categories": [
            "restaurant",
            "fast_food",
            "food_court",
            "cafe",
        ],
        "positive_terms": [
            "restaurant",
            "food",
            "kitchen",
            "grill",
            "cuisine",
            "dining",
            "cafe",
        ],
        "excluded_categories": [
            "hospital",
            "clinic",
            "dentist",
            "veterinary",
            "tailor",
            "laundry",
        ],
        "excluded_terms": [
            "clinic",
            "hospital",
            "medical",
            "dental",
            "veterinary",
            "tailor",
        ],
    },

    "cafe": {
        "aliases": [
            "coffee shop",
            "coffee",
        ],
        "allowed_categories": [
            "cafe",
            "restaurant",
        ],
        "positive_terms": [
            "cafe",
            "coffee",
            "espresso",
            "bakery",
        ],
        "excluded_categories": [
            "hospital",
            "clinic",
            "dentist",
            "veterinary",
            "tailor",
        ],
        "excluded_terms": [
            "clinic",
            "hospital",
            "medical",
            "dental",
            "veterinary",
            "tailor",
        ],
    },
}


def normalize_industry(
    industry: str,
) -> str:
    normalized = (
        str(industry or "")
        .strip()
        .lower()
        .replace("_", " ")
        .replace("-", " ")
    )

    for canonical_name, rules in INDUSTRY_RULES.items():
        aliases = rules.get(
            "aliases",
            [],
        )

        if (
            normalized == canonical_name
            or normalized in aliases
        ):
            return canonical_name

    return normalized


def get_industry_rules(
    industry: str,
) -> dict[str, Any]:
    normalized = normalize_industry(
        industry
    )

    return INDUSTRY_RULES.get(
        normalized,
        {
            "aliases": [],
            "allowed_categories": [
                normalized
            ] if normalized else [],
            "positive_terms": [
                normalized
            ] if normalized else [],
            "excluded_categories": [],
            "excluded_terms": [],
        },
    )   