import json
from datetime import datetime
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


def find_lead_by_name(
    db: Session,
    name: str,
) -> Lead | None:
    normalized_name = normalize_name(name)

    if not normalized_name:
        return None

    leads = db.query(Lead).all()

    return next(
        (
            lead
            for lead in leads
            if normalize_name(lead.name)
            == normalized_name
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
        incoming_value = values.get(field)
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
            db.refresh(existing_lead)

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