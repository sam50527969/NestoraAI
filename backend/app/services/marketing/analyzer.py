from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from typing import Any

from app.schemas.marketing import (
    MarketingBusinessAnalysis,
    MarketingBusinessProfile,
    MarketingGoal,
)
from app.services.prompt_loader import (
    PromptLoader,
    get_prompt_loader,
)


LLMCallable = Callable[
    [str, str],
    Awaitable[str | dict[str, Any]],
]


class MarketingAnalyzerError(RuntimeError):
    """Raised when the Marketing Analyzer cannot produce a valid result."""


class MarketingAnalyzer:
    """
    Analyzes a business profile and marketing goal.

    The service supports two operating modes:

    1. AI mode:
       An asynchronous LLM callable is supplied.

    2. Local fallback mode:
       Nestora creates a safe, structured analysis using the
       supplied business data without requiring an external API.

    This allows the Marketing Director package to remain usable
    during development even before an LLM provider is connected.
    """

    PROMPT_PATH = "marketing/business_analysis.md"

    def __init__(
        self,
        llm: LLMCallable | None = None,
        prompt_loader: PromptLoader | None = None,
    ) -> None:
        self._llm = llm
        self._prompt_loader = (
            prompt_loader or get_prompt_loader()
        )

    async def analyze(
        self,
        business: MarketingBusinessProfile,
        goal: MarketingGoal,
        additional_instructions: str | None = None,
    ) -> MarketingBusinessAnalysis:
        """
        Produce a structured business and marketing analysis.
        """

        if self._llm is None:
            return self._build_fallback_analysis(
                business=business,
                goal=goal,
                additional_instructions=additional_instructions,
            )

        system_prompt = self._prompt_loader.load(
            self.PROMPT_PATH
        )

        user_prompt = self._build_user_prompt(
            business=business,
            goal=goal,
            additional_instructions=additional_instructions,
        )

        try:
            raw_response = await self._llm(
                system_prompt,
                user_prompt,
            )

            response_data = self._parse_response(
                raw_response
            )

            return MarketingBusinessAnalysis.model_validate(
                response_data
            )

        except Exception as exc:
            raise MarketingAnalyzerError(
                "Marketing Analyzer failed to produce "
                "a valid structured analysis."
            ) from exc

    def _build_user_prompt(
        self,
        business: MarketingBusinessProfile,
        goal: MarketingGoal,
        additional_instructions: str | None,
    ) -> str:
        """
        Convert the validated request into a clear AI instruction.
        """

        payload = {
            "business": business.model_dump(
                mode="json"
            ),
            "marketing_goal": goal.model_dump(
                mode="json"
            ),
            "additional_instructions": (
                additional_instructions
            ),
        }

        return (
            "Analyze the following business and marketing goal.\n\n"
            "Use only the supplied information. Clearly treat "
            "missing information as an assumption.\n\n"
            f"{json.dumps(payload, indent=2, ensure_ascii=False)}"
        )

    @staticmethod
    def _parse_response(
        raw_response: str | dict[str, Any],
    ) -> dict[str, Any]:
        """
        Convert an LLM response into a Python dictionary.
        """

        if isinstance(raw_response, dict):
            return raw_response

        if not isinstance(raw_response, str):
            raise TypeError(
                "LLM response must be a string or dictionary."
            )

        cleaned_response = raw_response.strip()

        if cleaned_response.startswith("```"):
            cleaned_response = (
                MarketingAnalyzer._remove_code_fence(
                    cleaned_response
                )
            )

        parsed = json.loads(cleaned_response)

        if not isinstance(parsed, dict):
            raise ValueError(
                "Marketing analysis response must be a JSON object."
            )

        return parsed

    @staticmethod
    def _remove_code_fence(value: str) -> str:
        """
        Remove Markdown JSON fences when an AI provider adds them.
        """

        lines = value.strip().splitlines()

        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        return "\n".join(lines).strip()

    def _build_fallback_analysis(
        self,
        business: MarketingBusinessProfile,
        goal: MarketingGoal,
        additional_instructions: str | None,
    ) -> MarketingBusinessAnalysis:
        """
        Produce a useful local analysis when no LLM is connected.

        The fallback never invents competitors, market statistics,
        revenue data, or campaign performance.
        """

        services = self._clean_values(
            business.products_or_services
        )

        audiences = self._clean_values(
            business.target_audience
        )

        differentiators = self._clean_values(
            business.differentiators
        )

        channels = [
            channel.replace("_", " ").title()
            for channel in business.current_channels
        ]

        strengths: list[str] = []
        weaknesses: list[str] = []
        opportunities: list[str] = []
        risks: list[str] = []

        if services:
            strengths.append(
                "The business has clearly identified products or "
                "services that can be promoted through focused campaigns."
            )
        else:
            weaknesses.append(
                "The business has not yet provided a clear list of "
                "products or services, which may weaken campaign focus."
            )

        if audiences:
            strengths.append(
                "Target audience information is available, allowing "
                "marketing activity to be segmented more effectively."
            )
        else:
            weaknesses.append(
                "The target audience is not sufficiently defined."
            )

        if differentiators:
            strengths.append(
                "The business has stated differentiators that can be "
                "used in its positioning and campaign messages."
            )
        else:
            weaknesses.append(
                "No clear competitive differentiators were supplied."
            )

        if channels:
            strengths.append(
                "The business already has access to marketing channels: "
                + ", ".join(channels)
                + "."
            )
        else:
            opportunities.append(
                "Select a small number of measurable marketing channels "
                "rather than spreading effort across too many platforms."
            )

        if goal.monthly_budget > 0:
            opportunities.append(
                f"Use the stated monthly budget of "
                f"{goal.monthly_budget:,.2f} {goal.currency.upper()} "
                "for controlled campaign testing and optimization."
            )
        else:
            risks.append(
                "No paid marketing budget was supplied, so initial "
                "growth may depend mainly on organic activity and "
                "existing customer relationships."
            )

        if goal.timeline_days < 30:
            risks.append(
                "The requested timeline is short, so results may be "
                "limited and should be measured using early indicators."
            )
        elif goal.timeline_days <= 90:
            opportunities.append(
                "The timeline is suitable for running a focused campaign, "
                "measuring early results, and making adjustments."
            )
        else:
            opportunities.append(
                "The longer timeline allows testing, optimization, "
                "and improvement across multiple campaign cycles."
            )

        if business.preferred_languages:
            opportunities.append(
                "Create campaign content in the preferred languages: "
                + ", ".join(business.preferred_languages)
                + "."
            )

        if additional_instructions:
            opportunities.append(
                "The supplied additional instructions should be treated "
                "as an operating constraint during strategy development."
            )

        if not risks:
            risks.append(
                "Campaign performance data has not yet been supplied, "
                "so early projections must be treated as assumptions."
            )

        business_summary = self._business_summary(
            business=business,
            services=services,
        )

        audience_summary = self._audience_summary(
            audiences=audiences,
        )

        positioning = self._positioning(
            business=business,
            differentiators=differentiators,
            audiences=audiences,
        )

        confidence = self._calculate_confidence(
            business=business,
            goal=goal,
        )

        return MarketingBusinessAnalysis(
            business_summary=business_summary,
            audience_summary=audience_summary,
            strengths=strengths,
            weaknesses=weaknesses,
            opportunities=opportunities,
            risks=risks,
            recommended_positioning=positioning,
            confidence=confidence,
        )

    @staticmethod
    def _business_summary(
        business: MarketingBusinessProfile,
        services: list[str],
    ) -> str:
        location_text = (
            f" in {business.location}"
            if business.location
            else ""
        )

        service_text = (
            ", ".join(services)
            if services
            else "services that still require clearer definition"
        )

        description_text = (
            f" {business.description.strip()}"
            if business.description
            else ""
        )

        return (
            f"{business.business_name} is a "
            f"{business.industry} business{location_text} offering "
            f"{service_text}.{description_text}"
        ).strip()

    @staticmethod
    def _audience_summary(
        audiences: list[str],
    ) -> str:
        if audiences:
            return (
                "The stated target audience includes "
                + ", ".join(audiences)
                + ". Campaigns should separate these groups where "
                "their needs, intent, or preferred channels differ."
            )

        return (
            "The target audience has not yet been clearly defined. "
            "Audience research and customer segmentation should be "
            "completed before significant marketing spending."
        )

    @staticmethod
    def _positioning(
        business: MarketingBusinessProfile,
        differentiators: list[str],
        audiences: list[str],
    ) -> str:
        if differentiators and audiences:
            return (
                f"Position {business.business_name} as a trusted "
                f"{business.industry} provider for "
                f"{', '.join(audiences)}, emphasizing "
                f"{', '.join(differentiators)}."
            )

        if differentiators:
            return (
                f"Position {business.business_name} around its strongest "
                f"stated advantages: {', '.join(differentiators)}."
            )

        if audiences:
            return (
                f"Position {business.business_name} as a practical and "
                f"reliable {business.industry} provider focused on "
                f"{', '.join(audiences)}."
            )

        return (
            f"Position {business.business_name} as a reliable "
            f"{business.industry} provider, while first validating "
            "the primary customer segment and strongest differentiator."
        )

    @staticmethod
    def _calculate_confidence(
        business: MarketingBusinessProfile,
        goal: MarketingGoal,
    ) -> float:
        """
        Estimate confidence from the completeness of supplied data.
        """

        score = 0.45

        if business.description:
            score += 0.05

        if business.products_or_services:
            score += 0.10

        if business.target_audience:
            score += 0.10

        if business.differentiators:
            score += 0.10

        if business.current_channels:
            score += 0.05

        if business.location:
            score += 0.05

        if goal.monthly_budget > 0:
            score += 0.05

        return round(
            min(score, 0.90),
            2,
        )

    @staticmethod
    def _clean_values(
        values: list[str],
    ) -> list[str]:
        """
        Remove blank and duplicate values while retaining order.
        """

        cleaned: list[str] = []
        seen: set[str] = set()

        for value in values:
            normalized = value.strip()

            if not normalized:
                continue

            key = normalized.casefold()

            if key in seen:
                continue

            seen.add(key)
            cleaned.append(normalized)

        return cleaned


_marketing_analyzer = MarketingAnalyzer()


def get_marketing_analyzer() -> MarketingAnalyzer:
    """
    Return the shared Marketing Analyzer instance.
    """

    return _marketing_analyzer