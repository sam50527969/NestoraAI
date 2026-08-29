from __future__ import annotations

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.database.database import get_db
from app.database.models import BusinessMembership


def get_current_business_membership(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
) -> BusinessMembership:
    """
    Resolve the authenticated user's active
    business membership.

    A single active membership is required until
    explicit business selection is introduced.
    """

    memberships = (
        db.query(BusinessMembership)
        .filter(
            BusinessMembership.user_uid
            == current_user.user_uid,
            BusinessMembership.is_active.is_(
                True
            ),
        )
        .order_by(
            BusinessMembership.id.asc()
        )
        .all()
    )

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
                "Multiple active business "
                "memberships are available. "
                "Explicit business selection "
                "is required."
            ),
        )

    return memberships[0]


def get_current_business_uid(
    membership: BusinessMembership = Depends(
        get_current_business_membership
    ),
) -> str:
    return membership.business_uid
