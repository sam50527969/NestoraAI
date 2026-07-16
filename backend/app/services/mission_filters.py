PRIORITY_RANKS = {
    "low": 1,
    "medium": 2,
    "high": 3,
}


def has_real_value(value):
    if value is None:
        return False

    cleaned_value = str(value).strip()

    return bool(
        cleaned_value
        and cleaned_value.lower() != "not found"
    )


def is_valid_business_name(value):
    if not has_real_value(value):
        return False

    cleaned_value = str(value).strip().lower()

    return cleaned_value not in {
        "unknown business",
        "unknown",
        "unnamed business",
    }


def safe_integer(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def get_lead_quality(lead):
    return max(
        0,
        min(
            safe_integer(
                lead.get("opportunityScore"),
                default=0,
            ),
            100,
        ),
    )


def get_priority_rank(priority):
    normalized_priority = str(
        priority or "low"
    ).strip().lower()

    return PRIORITY_RANKS.get(
        normalized_priority,
        1,
    )


def passes_priority_filter(priority, priority_filter):
    normalized_filter = str(
        priority_filter or "all"
    ).strip().lower()

    if normalized_filter == "all":
        return True

    minimum_rank = PRIORITY_RANKS.get(
        normalized_filter,
        1,
    )

    return get_priority_rank(priority) >= minimum_rank


def filter_leads(
    leads,
    *,
    minimum_quality,
    priority_filter,
):
    accepted_leads = []

    safe_minimum_quality = max(
        0,
        min(
            safe_integer(
                minimum_quality,
                default=0,
            ),
            100,
        ),
    )

    for lead in leads:
        business_name = lead.get("businessName")
        priority = lead.get("priority") or "Low"
        quality = get_lead_quality(lead)

        if not is_valid_business_name(business_name):
            continue

        if quality < safe_minimum_quality:
            continue

        if not passes_priority_filter(
            priority,
            priority_filter,
        ):
            continue

        accepted_leads.append(lead)

    return accepted_leads