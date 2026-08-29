from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.auth.models import User
from app.database.models import (
    Business,
    BusinessMembership,
)


VALID_MEMBERSHIP_ROLES = {
    "owner",
    "admin",
    "member",
    "consultant",
}


def normalize_membership_role(
    role: str,
) -> str:
    cleaned = str(role or "").strip().lower()

    if cleaned not in VALID_MEMBERSHIP_ROLES:
        raise ValueError(
            "Membership role must be one of: "
            + ", ".join(
                sorted(VALID_MEMBERSHIP_ROLES)
            )
            + "."
        )

    return cleaned


def get_membership(
    db: Session,
    *,
    user_uid: str,
    business_uid: str,
) -> BusinessMembership | None:
    return (
        db.query(BusinessMembership)
        .filter(
            BusinessMembership.user_uid
            == user_uid.strip(),
            BusinessMembership.business_uid
            == business_uid.strip(),
        )
        .first()
    )


def add_membership(
    db: Session,
    *,
    user_uid: str,
    business_uid: str,
    role: str,
) -> BusinessMembership:
    """
    Add a membership to the current transaction.

    The caller owns commit or rollback.
    """

    clean_user_uid = str(
        user_uid or ""
    ).strip()

    clean_business_uid = str(
        business_uid or ""
    ).strip()

    if not clean_user_uid:
        raise ValueError(
            "User UID is required."
        )

    if not clean_business_uid:
        raise ValueError(
            "Business UID is required."
        )

    clean_role = normalize_membership_role(
        role
    )

    user = (
        db.query(User)
        .filter(
            User.user_uid == clean_user_uid
        )
        .first()
    )

    if user is None:
        raise ValueError(
            f"User '{clean_user_uid}' "
            "does not exist."
        )

    business = (
        db.query(Business)
        .filter(
            Business.business_uid
            == clean_business_uid
        )
        .first()
    )

    if business is None:
        raise ValueError(
            f"Business '{clean_business_uid}' "
            "does not exist."
        )

    existing = get_membership(
        db,
        user_uid=clean_user_uid,
        business_uid=clean_business_uid,
    )

    if existing is not None:
        raise ValueError(
            "This user already has a membership "
            "for this business."
        )

    membership = BusinessMembership(
        membership_uid=(
            f"mem_{uuid.uuid4().hex[:16]}"
        ),
        user_uid=clean_user_uid,
        business_uid=clean_business_uid,
        role=clean_role,
        is_active=True,
    )

    db.add(membership)
    db.flush()

    return membership


def create_membership(
    db: Session,
    *,
    user_uid: str,
    business_uid: str,
    role: str,
) -> BusinessMembership:
    clean_user_uid = str(
        user_uid or ""
    ).strip()

    clean_business_uid = str(
        business_uid or ""
    ).strip()

    if not clean_user_uid:
        raise ValueError(
            "User UID is required."
        )

    if not clean_business_uid:
        raise ValueError(
            "Business UID is required."
        )

    clean_role = normalize_membership_role(
        role
    )

    user = (
        db.query(User)
        .filter(
            User.user_uid == clean_user_uid
        )
        .first()
    )

    if user is None:
        raise ValueError(
            f"User '{clean_user_uid}' "
            "does not exist."
        )

    business = (
        db.query(Business)
        .filter(
            Business.business_uid
            == clean_business_uid
        )
        .first()
    )

    if business is None:
        raise ValueError(
            f"Business '{clean_business_uid}' "
            "does not exist."
        )

    existing = get_membership(
        db,
        user_uid=clean_user_uid,
        business_uid=clean_business_uid,
    )

    if existing is not None:
        raise ValueError(
            "This user already has a membership "
            "for this business."
        )

    membership = BusinessMembership(
        membership_uid=(
            f"mem_{uuid.uuid4().hex[:16]}"
        ),
        user_uid=clean_user_uid,
        business_uid=clean_business_uid,
        role=clean_role,
        is_active=True,
    )

    try:
        db.add(membership)
        db.commit()
        db.refresh(membership)
    except Exception:
        db.rollback()
        raise

    return membership


def list_user_memberships(
    db: Session,
    user_uid: str,
    *,
    active_only: bool = True,
) -> list[BusinessMembership]:
    query = (
        db.query(BusinessMembership)
        .filter(
            BusinessMembership.user_uid
            == user_uid.strip()
        )
    )

    if active_only:
        query = query.filter(
            BusinessMembership.is_active.is_(
                True
            )
        )

    return (
        query
        .order_by(
            BusinessMembership.id.asc()
        )
        .all()
    )


def user_can_access_business(
    db: Session,
    *,
    user_uid: str,
    business_uid: str,
) -> bool:
    membership = get_membership(
        db,
        user_uid=user_uid,
        business_uid=business_uid,
    )

    return bool(
        membership is not None
        and membership.is_active
    )
