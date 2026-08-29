from __future__ import annotations

from sqlalchemy.orm import Session

from app.business.models import BusinessProfile
from app.database.models import Business, BusinessMembership
from app.repositories.business_repository import BusinessRepository


class BusinessWorkspaceRepository:
    """
    Read businesses available to an authenticated workspace user.

    Workspace queries are membership-scoped and must never fall back
    to the global business collection.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self._business_repository = BusinessRepository(db)

    def list_for_user(
        self,
        *,
        user_uid: str,
        offset: int = 0,
        limit: int = 100,
    ) -> list[BusinessProfile]:
        clean_user_uid = str(user_uid or "").strip()

        if not clean_user_uid:
            return []

        safe_offset = max(offset, 0)
        safe_limit = min(max(limit, 1), 500)

        records = (
            self.db.query(Business)
            .join(
                BusinessMembership,
                BusinessMembership.business_uid
                == Business.business_uid,
            )
            .filter(
                BusinessMembership.user_uid
                == clean_user_uid,
                BusinessMembership.is_active.is_(True),
            )
            .order_by(Business.created_at.desc())
            .offset(safe_offset)
            .limit(safe_limit)
            .all()
        )

        return [
            self._business_repository.to_profile(record)
            for record in records
        ]

    def delete_workspace(
        self,
        *,
        business_uid: str,
    ) -> bool:
        """
        Delete a business and its memberships atomically.

        Memberships intentionally have no database foreign key,
        so workspace deletion explicitly removes them in the same
        transaction as the business.
        """

        clean_business_uid = str(
            business_uid or ""
        ).strip()

        if not clean_business_uid:
            return False

        record = (
            self.db.query(Business)
            .filter(
                Business.business_uid
                == clean_business_uid
            )
            .first()
        )

        if record is None:
            return False

        try:
            (
                self.db.query(BusinessMembership)
                .filter(
                    BusinessMembership.business_uid
                    == clean_business_uid
                )
                .delete(
                    synchronize_session=False
                )
            )

            self.db.delete(record)
            self.db.commit()

        except Exception:
            self.db.rollback()
            raise

        return True
