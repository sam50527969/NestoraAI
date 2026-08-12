import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.database.models import Lead
from app.schemas.crm import (
    LeadCreate,
    LeadUpdate,
)


VALID_STATUSES = {
    "New",
    "Contacted",
    "Qualified",
    "Won",
    "Lost",
}

ACTIVE_FOLLOW_UP_STATUSES = {
    "New",
    "Contacted",
    "Qualified",
}

VALID_PRIORITIES = {
    "Low",
    "Medium",
    "High",
}

EMPTY_VALUES = {
    "",
    "not found",
    "unknown",
    "unknown business",
    "n/a",
    "none",
    "null",
}


def normalize_name(
    value: Any,
) -> str:
    return " ".join(
        str(value or "")
        .strip()
        .casefold()
        .split()
    )


def has_useful_value(
    value: Any,
) -> bool:
    if value is None:
        return False

    if isinstance(value, str):
        return (
            normalize_name(value)
            not in EMPTY_VALUES
        )

    return True


def parse_datetime(
    value: Any,
) -> datetime | None:
    if not value:
        return None

    if isinstance(value, datetime):
        parsed_value = value
    else:
        cleaned_value = (
            str(value)
            .strip()
            .replace("Z", "+00:00")
        )

        if not cleaned_value:
            return None

        try:
            parsed_value = (
                datetime.fromisoformat(
                    cleaned_value
                )
            )
        except ValueError:
            return None

    if parsed_value.tzinfo is not None:
        parsed_value = (
            parsed_value
            .astimezone(timezone.utc)
            .replace(tzinfo=None)
        )

    return parsed_value


def find_lead_by_name(
    db: Session,
    name: str,
) -> Lead | None:
    normalized_name = normalize_name(
        name
    )

    if not normalized_name:
        return None

    leads = db.query(Lead).all()

    return next(
        (
            lead
            for lead in leads
            if normalize_name(
                lead.name
            ) == normalized_name
        ),
        None,
    )


def merge_lead_data(
    lead: Lead,
    values: dict[str, Any],
) -> bool:
    changed = False

    mergeable_fields = (
        "category",
        "address",
        "phone",
        "website",
        "latitude",
        "longitude",
        "source",
        "source_id",
    )

    for field in mergeable_fields:
        incoming_value = values.get(
            field
        )

        existing_value = getattr(
            lead,
            field,
            None,
        )

        if (
            not has_useful_value(
                existing_value
            )
            and has_useful_value(
                incoming_value
            )
        ):
            setattr(
                lead,
                field,
                incoming_value,
            )

            changed = True

    return changed


def create_lead(
    db: Session,
    lead_data: LeadCreate,
) -> Lead:
    values = lead_data.model_dump()

    name = str(
        values.get("name") or ""
    ).strip()

    if not name:
        raise ValueError(
            "Lead name is required"
        )

    existing_lead = find_lead_by_name(
        db,
        name,
    )

    if existing_lead is not None:
        changed = merge_lead_data(
            existing_lead,
            values,
        )

        if changed:
            db.commit()
            db.refresh(
                existing_lead
            )

        return existing_lead

    lead = Lead(
        **values,
    )

    db.add(lead)
    db.commit()
    db.refresh(lead)

    return lead


def get_leads(
    db: Session,
) -> list[Lead]:
    return (
        db.query(Lead)
        .order_by(
            Lead.created_at.desc(),
            Lead.id.desc(),
        )
        .all()
    )


def get_lead(
    db: Session,
    lead_id: int,
) -> Lead | None:
    return (
        db.query(Lead)
        .filter(
            Lead.id == lead_id
        )
        .first()
    )


def get_due_follow_ups(
    db: Session,
    limit: int = 100,
) -> list[Lead]:
    now = datetime.utcnow()

    candidates = (
        db.query(Lead)
        .filter(
            Lead.status.in_(
                ACTIVE_FOLLOW_UP_STATUSES
            ),
            Lead.next_follow_up.is_not(
                None
            ),
            Lead.next_follow_up != "",
        )
        .all()
    )

    due_leads = []

    for lead in candidates:
        follow_up_at = parse_datetime(
            lead.next_follow_up
        )

        if (
            follow_up_at is not None
            and follow_up_at <= now
        ):
            due_leads.append(
                (
                    follow_up_at,
                    lead,
                )
            )

    due_leads.sort(
        key=lambda item: (
            item[0],
            -(item[1].ai_score or 0),
            item[1].id,
        )
    )

    return [
        lead
        for _, lead in due_leads[
            :limit
        ]
    ]


def get_pipeline_summary(
    db: Session,
) -> dict[str, Any]:
    leads = db.query(Lead).all()

    status_counts = {
        status_name: 0
        for status_name in VALID_STATUSES
    }

    total_estimated_value = 0
    active_pipeline_value = 0
    weighted_pipeline_value = 0
    won_value = 0
    lost_value = 0

    active_statuses = {
        "New",
        "Contacted",
        "Qualified",
    }

    for lead in leads:
        status_name = str(
            lead.status or "New"
        ).strip().title()

        if status_name not in status_counts:
            status_name = "New"

        status_counts[status_name] += 1

        estimated_value = max(
            int(
                lead.estimated_value
                or 0
            ),
            0,
        )

        closing_probability = max(
            0,
            min(
                int(
                    lead.closing_probability
                    or 0
                ),
                100,
            ),
        )

        total_estimated_value += (
            estimated_value
        )

        if status_name in active_statuses:
            active_pipeline_value += (
                estimated_value
            )

            weighted_pipeline_value += round(
                estimated_value
                * closing_probability
                / 100
            )

        if status_name == "Won":
            won_value += estimated_value

        if status_name == "Lost":
            lost_value += estimated_value

    return {
        "total_leads": len(leads),
        "stages": {
            "new": status_counts["New"],
            "contacted": (
                status_counts["Contacted"]
            ),
            "qualified": (
                status_counts["Qualified"]
            ),
            "won": status_counts["Won"],
            "lost": status_counts["Lost"],
        },
        "total_estimated_value": (
            total_estimated_value
        ),
        "active_pipeline_value": (
            active_pipeline_value
        ),
        "weighted_pipeline_value": (
            weighted_pipeline_value
        ),
        "won_value": won_value,
        "lost_value": lost_value,
    }


def update_lead(
    db: Session,
    lead_id: int,
    lead_data: LeadUpdate,
) -> Lead | None:
    lead = get_lead(
        db,
        lead_id,
    )

    if not lead:
        return None

    update_values = (
        lead_data.model_dump(
            exclude_unset=True
        )
    )

    if (
        "status" in update_values
        and update_values["status"]
        not in VALID_STATUSES
    ):
        raise ValueError(
            "Invalid lead status"
        )

    if (
        "priority" in update_values
        and update_values["priority"]
        not in VALID_PRIORITIES
    ):
        raise ValueError(
            "Invalid lead priority"
        )

    for field, value in (
        update_values.items()
    ):
        setattr(
            lead,
            field,
            value,
        )

    db.commit()
    db.refresh(lead)

    return lead


def update_ai_analysis(
    db: Session,
    lead: Lead,
    analysis: dict,
) -> Lead:
    lead.ai_score = analysis.get(
        "score"
    )

    lead.ai_recommendation = (
        analysis.get(
            "recommendation"
        )
    )

    lead.ai_opportunity = (
        analysis.get(
            "opportunity"
        )
    )

    lead.ai_strengths = json.dumps(
        analysis.get(
            "strengths",
            [],
        ),
        ensure_ascii=False,
    )

    lead.ai_weaknesses = json.dumps(
        analysis.get(
            "weaknesses",
            [],
        ),
        ensure_ascii=False,
    )

    lead.ai_analyzed_at = (
        datetime.utcnow()
    )

    db.commit()
    db.refresh(lead)

    return lead