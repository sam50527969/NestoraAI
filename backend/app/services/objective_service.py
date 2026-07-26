from __future__ import annotations

import logging

from app.business.models import BusinessProfile
from app.objective.engine import (
    ObjectiveEngine,
    ObjectiveEngineResult,
)
from app.objective.exceptions import (
    ObjectiveError,
    ObjectiveExecutionError,
    ObjectiveValidationError,
)
from app.objective.models import BusinessObjective


logger = logging.getLogger(__name__)


class ObjectiveService:
    """
    Application service for processing business objectives.

    This service sits between API routes and the Objective Engine.

    Responsibilities:
    - Validate application-level consistency.
    - Coordinate the Objective Engine.
    - Provide logging.
    - Convert unexpected failures into objective-specific errors.
    """

    def __init__(
        self,
        engine: ObjectiveEngine | None = None,
    ) -> None:
        """
        Initialize the service.

        An ObjectiveEngine may be injected for testing or future
        configuration. If none is supplied, a default engine is used.
        """

        self._engine = engine or ObjectiveEngine()

    def process_objective(
        self,
        business: BusinessProfile,
        objective: BusinessObjective,
    ) -> ObjectiveEngineResult:
        """
        Analyze an objective and generate a strategy.

        This method does not execute the strategy. Execution will only
        begin after the owner approves the generated recommendation.
        """

        self._validate_request(
            business=business,
            objective=objective,
        )

        logger.info(
            "Processing objective '%s' for business '%s'.",
            objective.id,
            business.id,
        )

        try:
            result = self._engine.process(
                business=business,
                objective=objective,
            )

            logger.info(
                (
                    "Objective '%s' processed successfully. "
                    "Opportunities: %s. Strategy: '%s'."
                ),
                objective.id,
                result.analysis.opportunity_count,
                result.strategy.title,
            )

            return result

        except ObjectiveError:
            logger.exception(
                "Objective processing failed for '%s'.",
                objective.id,
            )
            raise

        except Exception as exc:
            logger.exception(
                "Unexpected objective service failure for '%s'.",
                objective.id,
            )

            raise ObjectiveExecutionError(
                "The objective could not be processed."
            ) from exc

    @staticmethod
    def _validate_request(
        business: BusinessProfile,
        objective: BusinessObjective,
    ) -> None:
        """
        Validate relationships between the business and objective.
        """

        if business is None:
            raise ObjectiveValidationError(
                "Business profile is required."
            )

        if objective is None:
            raise ObjectiveValidationError(
                "Business objective is required."
            )

        business.validate()
        objective.validate()

        if (
            objective.business_id is not None
            and objective.business_id != business.id
        ):
            raise ObjectiveValidationError(
                "The objective belongs to a different business."
            )