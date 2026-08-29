from __future__ import annotations

import json
from typing import Any

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.business.context import BusinessContext
from app.business.models import (
    BusinessProfile,
    BusinessSize,
    BusinessTeam,
    CustomerProfile,
    FinancialProfile,
    IndustryType,
    OperationalProfile,
    WorkingHours,
)
from app.database.models import Business


class BusinessRepository:
    """
    Data-access layer for business profiles.

    Converts between SQLAlchemy Business records and
    BusinessProfile domain objects.
    """

    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    def add(
        self,
        business: BusinessProfile,
    ) -> Business:
        """
        Add a business to the current transaction.

        The caller owns commit or rollback. This is intended
        for atomic workflows that persist a business together
        with related records.
        """

        business.validate()

        if self.exists(business.id):
            raise ValueError(
                f"Business '{business.id}' already exists."
            )

        record = Business(
            business_uid=business.id,
        )

        self._apply_profile(
            record=record,
            business=business,
        )

        try:
            self.db.add(record)
            self.db.flush()

        except IntegrityError as exc:
            raise ValueError(
                f"Business '{business.id}' already exists."
            ) from exc

        except SQLAlchemyError as exc:
            raise RuntimeError(
                "The business could not be created."
            ) from exc

        return record

    def create(
        self,
        business: BusinessProfile,
    ) -> BusinessProfile:
        """
        Create and persist a new business profile.
        """

        business.validate()

        if self.exists(business.id):
            raise ValueError(
                f"Business '{business.id}' already exists."
            )

        record = Business(
            business_uid=business.id,
        )

        self._apply_profile(
            record=record,
            business=business,
        )

        try:
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)

        except IntegrityError as exc:
            self.db.rollback()

            raise ValueError(
                f"Business '{business.id}' already exists."
            ) from exc

        except SQLAlchemyError as exc:
            self.db.rollback()

            raise RuntimeError(
                "The business could not be created."
            ) from exc

        return self.to_profile(record)

    def get_by_uid(
        self,
        business_uid: str,
    ) -> BusinessProfile | None:
        """
        Retrieve one business using its public UID.
        """

        record = self._get_record_by_uid(
            business_uid,
        )

        if record is None:
            return None

        return self.to_profile(record)

    def get_context(
        self,
        business_uid: str,
    ) -> BusinessContext | None:
        """
        Return canonical execution context for one business.
        """

        business = self.get_by_uid(business_uid)

        if business is None:
            return None

        return BusinessContext.from_business(business)

    def get_all(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> list[BusinessProfile]:
        """
        Return paginated business profiles.
        """

        safe_offset = max(offset, 0)
        safe_limit = min(max(limit, 1), 500)

        records = (
            self.db.query(Business)
            .order_by(Business.created_at.desc())
            .offset(safe_offset)
            .limit(safe_limit)
            .all()
        )

        return [
            self.to_profile(record)
            for record in records
        ]

    def update(
        self,
        business: BusinessProfile,
    ) -> BusinessProfile | None:
        """
        Update an existing business profile.
        """

        business.validate()

        record = self._get_record_by_uid(
            business.id,
        )

        if record is None:
            return None

        self._apply_profile(
            record=record,
            business=business,
        )

        try:
            self.db.commit()
            self.db.refresh(record)

        except IntegrityError as exc:
            self.db.rollback()

            raise ValueError(
                "The business update conflicts with an existing record."
            ) from exc

        except SQLAlchemyError as exc:
            self.db.rollback()

            raise RuntimeError(
                "The business could not be updated."
            ) from exc

        return self.to_profile(record)

    def delete(
        self,
        business_uid: str,
    ) -> bool:
        """
        Delete a business profile.
        """

        record = self._get_record_by_uid(
            business_uid,
        )

        if record is None:
            return False

        try:
            self.db.delete(record)
            self.db.commit()

        except SQLAlchemyError as exc:
            self.db.rollback()

            raise RuntimeError(
                "The business could not be deleted."
            ) from exc

        return True

    def exists(
        self,
        business_uid: str,
    ) -> bool:
        """
        Check whether a business UID exists.
        """

        if not business_uid or not business_uid.strip():
            return False

        record = (
            self.db.query(Business.id)
            .filter(
                Business.business_uid
                == business_uid.strip()
            )
            .first()
        )

        return record is not None

    def _get_record_by_uid(
        self,
        business_uid: str,
    ) -> Business | None:
        """
        Retrieve the SQLAlchemy Business record.
        """

        if not business_uid or not business_uid.strip():
            return None

        return (
            self.db.query(Business)
            .filter(
                Business.business_uid
                == business_uid.strip()
            )
            .first()
        )

    @classmethod
    def to_profile(
        cls,
        record: Business,
    ) -> BusinessProfile:
        """
        Convert a database record into a BusinessProfile.
        """

        working_hours_data = cls._deserialize_json(
            record.working_hours,
            default=[],
        )

        working_hours = []

        for item in working_hours_data:
            if not isinstance(item, dict):
                continue

            day = str(item.get("day", "")).strip()

            if not day:
                continue

            working_hours.append(
                WorkingHours(
                    day=day,
                    opens_at=item.get("opens_at"),
                    closes_at=item.get("closes_at"),
                    is_closed=bool(
                        item.get("is_closed", False)
                    ),
                )
            )

        return BusinessProfile(
            id=record.business_uid,
            name=record.name,
            industry=IndustryType(record.industry),
            country=record.country,
            city=record.city,
            region=record.region,
            timezone=record.timezone,
            locale=record.locale,
            size=BusinessSize(record.size),
            description=record.description or "",
            team=BusinessTeam(
                employee_count=record.employee_count,
                departments=cls._deserialize_json(
                    record.departments,
                    default=[],
                ),
                roles=cls._deserialize_json(
                    record.roles,
                    default={},
                ),
            ),
            customers=CustomerProfile(
                total_customers=record.total_customers,
                active_customers=record.active_customers,
                inactive_customers=record.inactive_customers,
                average_monthly_customers=(
                    record.average_monthly_customers
                ),
                returning_customer_rate=(
                    record.returning_customer_rate
                ),
                average_customer_value=(
                    record.average_customer_value
                ),
            ),
            finances=FinancialProfile(
                currency=record.currency,
                monthly_revenue=record.monthly_revenue,
                monthly_expenses=record.monthly_expenses,
                average_transaction_value=(
                    record.average_transaction_value
                ),
                marketing_budget=(
                    record.marketing_budget
                ),
                outstanding_receivables=(
                    record.outstanding_receivables
                ),
            ),
            operations=OperationalProfile(
                daily_capacity=record.daily_capacity,
                average_daily_volume=(
                    record.average_daily_volume
                ),
                cancellation_rate=(
                    record.cancellation_rate
                ),
                utilization_rate=(
                    record.utilization_rate
                ),
                locations_count=(
                    record.locations_count
                ),
                working_hours=working_hours,
            ),
            goals=cls._deserialize_json(
                record.goals,
                default=[],
            ),
            metadata=cls._deserialize_json(
                record.metadata_json,
                default={},
            ),
            created_at=record.created_at,
            updated_at=record.updated_at,
        )

    @classmethod
    def _apply_profile(
        cls,
        record: Business,
        business: BusinessProfile,
    ) -> None:
        """
        Copy BusinessProfile values into an ORM record.
        """

        record.business_uid = business.id.strip()
        record.name = business.name.strip()
        record.industry = cls._enum_value(
            business.industry
        )
        record.country = business.country.strip()
        record.city = cls._clean_optional_text(
            business.city
        )
        record.region = cls._clean_optional_text(
            business.region
        )
        record.timezone = cls._clean_optional_text(
            business.timezone
        )
        record.locale = cls._clean_optional_text(
            business.locale
        )
        record.size = cls._enum_value(
            business.size
        )
        record.description = business.description or ""

        record.employee_count = (
            business.team.employee_count
        )
        record.departments = cls._serialize_json(
            business.team.departments
        )
        record.roles = cls._serialize_json(
            business.team.roles
        )

        record.total_customers = (
            business.customers.total_customers
        )
        record.active_customers = (
            business.customers.active_customers
        )
        record.inactive_customers = (
            business.customers.inactive_customers
        )
        record.average_monthly_customers = (
            business.customers.average_monthly_customers
        )
        record.returning_customer_rate = (
            business.customers.returning_customer_rate
        )
        record.average_customer_value = (
            business.customers.average_customer_value
        )

        record.currency = (
            business.finances.currency
        )
        record.monthly_revenue = (
            business.finances.monthly_revenue
        )
        record.monthly_expenses = (
            business.finances.monthly_expenses
        )
        record.average_transaction_value = (
            business.finances.average_transaction_value
        )
        record.marketing_budget = (
            business.finances.marketing_budget
        )
        record.outstanding_receivables = (
            business.finances.outstanding_receivables
        )

        record.daily_capacity = (
            business.operations.daily_capacity
        )
        record.average_daily_volume = (
            business.operations.average_daily_volume
        )
        record.cancellation_rate = (
            business.operations.cancellation_rate
        )
        record.utilization_rate = (
            business.operations.utilization_rate
        )
        record.locations_count = (
            business.operations.locations_count
        )

        record.working_hours = cls._serialize_json(
            [
                {
                    "day": item.day,
                    "opens_at": item.opens_at,
                    "closes_at": item.closes_at,
                    "is_closed": item.is_closed,
                }
                for item in business.operations.working_hours
            ]
        )

        record.goals = cls._serialize_json(
            business.goals
        )
        record.metadata_json = cls._serialize_json(
            business.metadata
        )

    @staticmethod
    def _clean_optional_text(
        value: str | None,
    ) -> str | None:
        """
        Normalize optional business context text.
        """

        if value is None:
            return None

        cleaned = value.strip()

        return cleaned or None

    @staticmethod
    def _enum_value(
        value: Any,
    ) -> str:
        """
        Return the string value of an enum or string.
        """

        enum_value = getattr(
            value,
            "value",
            value,
        )

        return str(enum_value)

    @staticmethod
    def _serialize_json(
        value: Any,
    ) -> str:
        """
        Serialize data for Text database columns.
        """

        return json.dumps(
            value,
            ensure_ascii=False,
            separators=(",", ":"),
        )

    @staticmethod
    def _deserialize_json(
        value: str | None,
        *,
        default: Any,
    ) -> Any:
        """
        Safely deserialize JSON from a Text column.
        """

        if not value:
            return default

        try:
            return json.loads(value)

        except (
            TypeError,
            json.JSONDecodeError,
        ):
            return default