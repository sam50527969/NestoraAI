from __future__ import annotations

from app.business.models import BusinessProfile
from app.objective.exceptions import (
    BusinessProfileRequiredError,
    ObjectiveAnalysisError,
)
from app.objective.models import (
    BusinessObjective,
    BusinessOpportunity,
    ObjectiveAnalysisResult,
)


class ObjectiveAnalyzer:
    """
    First stage of the AI CEO.

    Responsible for analyzing a business objective together
    with the current business profile and identifying
    business opportunities before strategy generation.
    """

    def analyze(
        self,
        business: BusinessProfile,
        objective: BusinessObjective,
    ) -> ObjectiveAnalysisResult:
        """
        Analyze the business objective.

        Returns an ObjectiveAnalysisResult that can be
        consumed by the Strategist.
        """

        if business is None:
            raise BusinessProfileRequiredError(
                "Business profile is required."
            )

        objective.validate()
        business.validate()

        opportunities: list[BusinessOpportunity] = []

        observations: list[str] = []

        recommended_executives: set[str] = set()

        try:

            title = objective.title.lower()

            #
            # Revenue Growth
            #

            if "revenue" in title or "income" in title:

                opportunities.append(
                    BusinessOpportunity(
                        title="Recover inactive customers",
                        description=(
                            "Recover inactive customers before "
                            "spending additional marketing budget."
                        ),
                        estimated_value=25000,
                        confidence=0.94,
                        executives=[
                            "Marketing",
                            "Follow-up",
                            "Reception",
                        ],
                        reasoning=[
                            "Recovering existing customers usually "
                            "costs less than acquiring new ones."
                        ],
                    )
                )

                observations.append(
                    "Revenue growth objective detected."
                )

                recommended_executives.update(
                    [
                        "Marketing",
                        "Follow-up",
                        "Reception",
                    ]
                )

            #
            # Customer Growth
            #

            if "customer" in title or "patient" in title:

                opportunities.append(
                    BusinessOpportunity(
                        title="Increase customer retention",
                        description=(
                            "Focus on returning customers before "
                            "expanding acquisition."
                        ),
                        estimated_value=18000,
                        confidence=0.90,
                        executives=[
                            "Marketing",
                            "Customer Success",
                        ],
                        reasoning=[
                            "Returning customers increase lifetime value."
                        ],
                    )
                )

                observations.append(
                    "Customer growth objective detected."
                )

                recommended_executives.update(
                    [
                        "Marketing",
                        "Customer Success",
                    ]
                )

            #
            # General fallback
            #

            if not opportunities:

                opportunities.append(
                    BusinessOpportunity(
                        title="General business review",
                        description=(
                            "Further business analysis is required."
                        ),
                        estimated_value=0,
                        confidence=0.60,
                    )
                )

                observations.append(
                    "No specialized analyzer rule matched."
                )

            confidence = (
                sum(
                    o.confidence
                    for o in opportunities
                )
                / len(opportunities)
            )

            return ObjectiveAnalysisResult(
                objective=objective,
                opportunities=opportunities,
                observations=observations,
                recommended_executives=sorted(
                    recommended_executives
                ),
                confidence=confidence,
                ready_for_strategy=True,
            )

        except Exception as exc:

            raise ObjectiveAnalysisError(
                str(exc)
            ) from exc