from __future__ import annotations

from sqlalchemy.orm import Session

from app.business.models import BusinessProfile
from app.database.models import BusinessMembership
from app.repositories.business_repository import (
    BusinessRepository,
)
from app.services.business_membership_service import (
    add_membership,
)


class BusinessOnboardingService:
    """
    Atomically create a business and its owner membership.
    """

    def __init__(
        self,
        db: Session,
    ) -> None:
        self._db = db
        self._repository = BusinessRepository(db)

    def create_business_for_owner(
        self,
        *,
        business: BusinessProfile,
        owner_user_uid: str,
    ) -> tuple[BusinessProfile, BusinessMembership]:
        """
        Create a business and owner membership in one transaction.
        """

        try:
            record = self._repository.add(
                business
            )

            membership = add_membership(
                self._db,
                user_uid=owner_user_uid,
                business_uid=business.id,
                role="owner",
            )

            self._db.commit()

            self._db.refresh(record)
            self._db.refresh(membership)

        except Exception:
            self._db.rollback()
            raise

        return (
            self._repository.get_by_uid(
                business.id
            ),
            membership,
        )
