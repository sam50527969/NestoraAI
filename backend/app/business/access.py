from __future__ import annotations

from fastapi import (
    Depends,
    Header,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.database.database import get_db
from app.database.models import BusinessMembership


def resolve_business_membership(
    db: Session,
    *,
    user_uid: str,
    selected_business_uid: str | None = None,
) -> BusinessMembership:
    """Resolve active workspace membership for HTTP or realtime use."""

    clean_business_uid = str(
        selected_business_uid or ""
    ).strip()

    query = db.query(BusinessMembership).filter(
        BusinessMembership.user_uid == user_uid,
        BusinessMembership.is_active.is_(True),
    )

    if clean_business_uid:
        membership = query.filter(
            BusinessMembership.business_uid == clean_business_uid
        ).first()

        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "The selected business workspace "
                    "is not available for this account."
                ),
            )

        return membership

    memberships = query.order_by(
        BusinessMembership.id.asc()
    ).limit(2).all()

    if not memberships:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "No active business membership "
                "is available for this account."
            ),
        )

    if len(memberships) > 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Multiple active business memberships are available. "
                "Send X-Business-Uid to select the active workspace."
            ),
        )

    return memberships[0]


def get_current_business_membership(
    selected_business_uid: str | None = Header(
        default=None,
        alias="X-Business-Uid",
    ),
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
) -> BusinessMembership:
    """
    Resolve and validate the authenticated user's
    active business workspace.

    Explicit selection is required when more than
    one active membership exists. A single active
    membership remains a safe compatibility fallback.
    """

    return resolve_business_membership(
        db,
        user_uid=current_user.user_uid,
        selected_business_uid=selected_business_uid,
    )


def get_current_business_uid(
    membership: BusinessMembership = Depends(
        get_current_business_membership
    ),
) -> str:
    return membership.business_uid
