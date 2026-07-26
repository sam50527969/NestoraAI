from __future__ import annotations

import logging

from app.business.models import BusinessProfile
from app.repositories.business_repository import BusinessRepository

logger = logging.getLogger(__name__)


class BusinessService:
    """
    Application service responsible for business lifecycle management.

    This service sits between API routes and the BusinessRepository.

    Responsibilities:
    - Validate business profiles.
    - Prevent duplicate businesses.
    - Coordinate repository operations.
    - Provide logging.
    - Centralize business-related rules.
    """

    def __init__(
        self,
        repository: BusinessRepository,
    ) -> None:
        self._repository = repository

    def create_business(
        self,
        business: BusinessProfile,
    ) -> BusinessProfile:
        """
        Create a new business.
        """

        business.validate()

        logger.info(
            "Creating business '%s'.",
            business.id,
        )

        created = self._repository.create(business)

        logger.info(
            "Business '%s' created successfully.",
            created.id,
        )

        return created

    def get_business(
        self,
        business_uid: str,
    ) -> BusinessProfile | None:
        """
        Retrieve a business by its public UID.
        """

        return self._repository.get_by_uid(
            business_uid,
        )

    def list_businesses(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> list[BusinessProfile]:
        """
        Return paginated business profiles.
        """

        return self._repository.get_all(
            offset=offset,
            limit=limit,
        )

    def update_business(
        self,
        business: BusinessProfile,
    ) -> BusinessProfile | None:
        """
        Update an existing business.
        """

        business.validate()

        logger.info(
            "Updating business '%s'.",
            business.id,
        )

        updated = self._repository.update(
            business,
        )

        if updated is not None:
            logger.info(
                "Business '%s' updated.",
                updated.id,
            )

        return updated

    def delete_business(
        self,
        business_uid: str,
    ) -> bool:
        """
        Delete a business.
        """

        logger.info(
            "Deleting business '%s'.",
            business_uid,
        )

        deleted = self._repository.delete(
            business_uid,
        )

        if deleted:
            logger.info(
                "Business '%s' deleted.",
                business_uid,
            )

        return deleted

    def ensure_business_exists(
        self,
        business_uid: str,
    ) -> BusinessProfile:
        """
        Retrieve a business or raise an error.
        """

        business = self.get_business(
            business_uid,
        )

        if business is None:
            raise ValueError(
                f"Business '{business_uid}' does not exist."
            )

        return business