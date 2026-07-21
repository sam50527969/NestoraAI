from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from typing import Any

from app.schemas.marketing import (
    MarketingBusinessAnalysis,
    MarketingBusinessProfile,
    MarketingChannel,
    MarketingChannelStrategy,
    MarketingGoal,
    MarketingStrategy,
)
from app.services.prompt_loader import (
    PromptLoader,
    get_prompt_loader,
)


LLMCallable = Callable[
    [str, str],
    Awaitable[str | dict[str, Any]],
]


class MarketingStrategistError(RuntimeError):
    """Raised when a valid marketing strategy cannot be produced."""


class MarketingStrategist:
    """
    Converts a business analysis and goal into a structured
    marketing strategy.

    The strategist supports:

    - AI mode when an LLM callable is supplied.
    - Local fallback mode during development.
    """

    PROMPT_PATH = "marketing/strategy.md"

    DEFAULT_CHANNEL_PRIORITY: tuple[
        MarketingChannel,
        ...,
    ] = (
        "google_business",
        "whatsapp",
        "instagram",
        "facebook",
        "google_ads",
        "email",
        "linkedin",
        "tiktok",
        "x",
    )

    def __init__(
        self,
        llm: LLMCallable | None = None,
        prompt_loader: PromptLoader | None = None,
    ) -> None:
        self._llm = llm
        self._prompt_loader = (
            prompt_loader or get_prompt_loader()
        )

    async def create_strategy(
        self,
        business: MarketingBusinessProfile,
        goal: MarketingGoal,
        analysis: MarketingBusinessAnalysis,
        additional_instructions: str | None = None,
    ) -> MarketingStrategy:
        """
        Create a structured marketing strategy.
        """

        if self._llm is None:
            return self._build_fallback_strategy(
                business=business,
                goal=goal,
                analysis=analysis,
                additional_instructions=additional_instructions,
            )

        system_prompt = self._prompt_loader.load(
            self.PROMPT_PATH
        )

        user_prompt = self._build_user_prompt(
            business=business,
            goal=goal,
            analysis=analysis,
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

            strategy = MarketingStrategy.model_validate(
                response_data
            )

            self._validate_budget_percentages(
                strategy
            )

            return strategy

        except Exception as exc:
            raise MarketingStrategistError(
                "Marketing Strategist failed to produce "
                "a valid structured strategy."
            ) from exc

    def _build_user_prompt(
        self,
        business: MarketingBusinessProfile,
        goal: MarketingGoal,
        analysis: MarketingBusinessAnalysis,
        additional_instructions: str | None,
    ) -> str:
        payload = {
            "business": business.model_dump(
                mode="json"
            ),
            "goal": goal.model_dump(
                mode="json"
            ),
            "business_analysis": analysis.model_dump(
                mode="json"
            ),
            "additional_instructions": (
                additional_instructions
            ),
        }

        return (
            "Create a practical marketing strategy using the "
            "validated business profile, goal, and analysis below.\n\n"
            "The total budget percentages across all selected channels "
            "must equal 100.\n\n"
            f"{json.dumps(payload, indent=2, ensure_ascii=False)}"
        )

    @staticmethod
    def _parse_response(
        raw_response: str | dict[str, Any],
    ) -> dict[str, Any]:
        if isinstance(raw_response, dict):
            return raw_response

        if not isinstance(raw_response, str):
            raise TypeError(
                "LLM response must be a string or dictionary."
            )

        cleaned_response = raw_response.strip()

        if cleaned_response.startswith("```"):
            cleaned_response = (
                MarketingStrategist._remove_code_fence(
                    cleaned_response
                )
            )

        parsed = json.loads(cleaned_response)

        if not isinstance(parsed, dict):
            raise ValueError(
                "Marketing strategy response must be a JSON object."
            )

        return parsed

    @staticmethod
    def _remove_code_fence(
        value: str,
    ) -> str:
        lines = value.strip().splitlines()

        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        return "\n".join(lines).strip()

    def _build_fallback_strategy(
        self,
        business: MarketingBusinessProfile,
        goal: MarketingGoal,
        analysis: MarketingBusinessAnalysis,
        additional_instructions: str | None,
    ) -> MarketingStrategy:
        channels = self._select_channels(
            business=business,
            goal=goal,
        )

        percentages = self._allocate_percentages(
            channels=channels,
            has_budget=goal.monthly_budget > 0,
        )

        estimated_total_leads = self._estimate_total_leads(
            goal=goal,
            channels=channels,
        )

        channel_strategies: list[
            MarketingChannelStrategy
        ] = []

        remaining_leads = estimated_total_leads

        for index, channel in enumerate(channels):
            percentage = percentages[channel]

            if index == len(channels) - 1:
                expected_leads = remaining_leads
            else:
                expected_leads = round(
                    estimated_total_leads
                    * percentage
                    / 100
                )
                remaining_leads -= expected_leads

            channel_strategies.append(
                MarketingChannelStrategy(
                    channel=channel,
                    objective=self._channel_objective(
                        channel=channel,
                        goal=goal,
                    ),
                    rationale=self._channel_rationale(
                        channel=channel,
                        business=business,
                    ),
                    content_types=self._content_types(
                        channel
                    ),
                    posting_frequency=(
                        self._posting_frequency(
                            channel
                        )
                    ),
                    budget_percentage=percentage,
                    expected_leads=max(
                        expected_leads,
                        0,
                    ),
                )
            )

        target_segments = (
            self._clean_values(
                business.target_audience
            )
            or [
                (
                    "Prospective customers who match "
                    "the business's primary service offering"
                )
            ]
        )

        key_messages = self._build_key_messages(
            business=business,
            analysis=analysis,
        )

        success_metrics = [
            "Qualified enquiries generated",
            "Cost per qualified lead",
            "Conversion rate from enquiry to customer",
            "Follow-up response rate",
            "Campaign return on investment",
        ]

        risks = list(analysis.risks)

        if not business.current_channels:
            risks.append(
                "New marketing channels may require setup, "
                "content preparation, and initial testing."
            )

        if goal.monthly_budget <= 0:
            risks.append(
                "Organic-only execution may take longer to generate "
                "measurable results."
            )

        if additional_instructions:
            risks.append(
                "Execution must remain consistent with the supplied "
                "additional operating instructions."
            )

        confidence = round(
            min(
                analysis.confidence + 0.03,
                0.90,
            ),
            2,
        )

        return MarketingStrategy(
            strategy_name=(
                f"{business.business_name} "
                f"{goal.timeline_days}-Day Growth Strategy"
            ),
            executive_summary=(
                f"This strategy is designed to support the objective "
                f"of {goal.objective}. It prioritizes a focused set "
                f"of measurable channels, clear customer messaging, "
                f"consistent follow-up, and regular performance review."
            ),
            primary_objective=goal.objective,
            target_segments=target_segments,
            key_messages=key_messages,
            channels=channel_strategies,
            success_metrics=success_metrics,
            risks=self._deduplicate(risks),
            confidence=confidence,
        )

    def _select_channels(
        self,
        business: MarketingBusinessProfile,
        goal: MarketingGoal,
    ) -> list[MarketingChannel]:
        preferred = self._unique_channels(
            goal.preferred_channels
        )

        current = self._unique_channels(
            business.current_channels
        )

        selected: list[MarketingChannel] = []

        for channel in preferred + current:
            if channel not in selected:
                selected.append(channel)

        for channel in self._industry_channels(
            business.industry
        ):
            if channel not in selected:
                selected.append(channel)

        for channel in self.DEFAULT_CHANNEL_PRIORITY:
            if channel not in selected:
                selected.append(channel)

        channel_limit = (
            4
            if goal.monthly_budget >= 3000
            else 3
        )

        if goal.monthly_budget <= 0:
            channel_limit = 3

        return selected[:channel_limit]

    @staticmethod
    def _industry_channels(
        industry: str,
    ) -> list[MarketingChannel]:
        normalized = industry.strip().casefold()

        if any(
            value in normalized
            for value in (
                "health",
                "clinic",
                "medical",
                "dental",
                "beauty",
            )
        ):
            return [
                "google_business",
                "instagram",
                "whatsapp",
                "google_ads",
            ]

        if any(
            value in normalized
            for value in (
                "professional",
                "consulting",
                "software",
                "technology",
                "business",
            )
        ):
            return [
                "linkedin",
                "email",
                "google_ads",
                "google_business",
            ]

        if any(
            value in normalized
            for value in (
                "retail",
                "restaurant",
                "food",
                "fashion",
                "home",
            )
        ):
            return [
                "instagram",
                "facebook",
                "google_business",
                "whatsapp",
            ]

        return [
            "google_business",
            "instagram",
            "whatsapp",
        ]

    @staticmethod
    def _allocate_percentages(
        channels: list[MarketingChannel],
        has_budget: bool,
    ) -> dict[MarketingChannel, float]:
        if not channels:
            return {}

        if len(channels) == 1:
            return {
                channels[0]: 100.0,
            }

        if len(channels) == 2:
            values = [60.0, 40.0]

        elif len(channels) == 3:
            values = [45.0, 35.0, 20.0]

        else:
            values = [35.0, 30.0, 20.0, 15.0]

        if not has_budget:
            values = MarketingStrategist._equal_percentages(
                len(channels)
            )

        return {
            channel: values[index]
            for index, channel in enumerate(channels)
        }

    @staticmethod
    def _equal_percentages(
        count: int,
    ) -> list[float]:
        if count <= 0:
            return []

        base = round(
            100 / count,
            2,
        )

        percentages = [
            base
            for _ in range(count)
        ]

        difference = round(
            100 - sum(percentages),
            2,
        )

        percentages[-1] = round(
            percentages[-1] + difference,
            2,
        )

        return percentages

    @staticmethod
    def _estimate_total_leads(
        goal: MarketingGoal,
        channels: list[MarketingChannel],
    ) -> int:
        if goal.monthly_budget <= 0:
            return max(
                len(channels) * 3,
                6,
            )

        conservative_cost_per_lead = 125

        estimated = int(
            goal.monthly_budget
            / conservative_cost_per_lead
        )

        return max(
            estimated,
            len(channels),
        )

    @staticmethod
    def _channel_objective(
        channel: MarketingChannel,
        goal: MarketingGoal,
    ) -> str:
        objectives: dict[
            MarketingChannel,
            str,
        ] = {
            "google_business": (
                "Increase local discovery and convert "
                "high-intent searches into enquiries."
            ),
            "google_ads": (
                "Capture customers actively searching for "
                "the relevant products or services."
            ),
            "instagram": (
                "Build awareness, trust, and engagement through "
                "visual and educational content."
            ),
            "facebook": (
                "Reach local audience segments and support "
                "community-focused promotion."
            ),
            "whatsapp": (
                "Convert enquiries and re-engage existing contacts "
                "through timely direct follow-up."
            ),
            "email": (
                "Nurture prospects and existing customers using "
                "structured campaigns and offers."
            ),
            "linkedin": (
                "Build professional credibility and reach "
                "business decision-makers."
            ),
            "tiktok": (
                "Generate awareness through short-form, "
                "high-attention content."
            ),
            "x": (
                "Support timely updates, authority building, "
                "and audience engagement."
            ),
        }

        return objectives.get(
            channel,
            goal.objective,
        )

    @staticmethod
    def _channel_rationale(
        channel: MarketingChannel,
        business: MarketingBusinessProfile,
    ) -> str:
        current = channel in business.current_channels

        prefix = (
            "The business already uses this channel. "
            if current
            else "This channel can add a new measurable route "
            "to potential customers. "
        )

        rationales: dict[
            MarketingChannel,
            str,
        ] = {
            "google_business": (
                "It supports local visibility, customer trust, "
                "directions, calls, and high-intent discovery."
            ),
            "google_ads": (
                "It can reach customers when they are actively "
                "searching for a relevant service."
            ),
            "instagram": (
                "It is suitable for visual proof, educational "
                "content, testimonials, and brand awareness."
            ),
            "facebook": (
                "It supports local targeting, community visibility, "
                "and retargeting opportunities."
            ),
            "whatsapp": (
                "It supports direct communication, reminders, "
                "lead qualification, and customer follow-up."
            ),
            "email": (
                "It provides a controlled channel for nurturing, "
                "education, retention, and reactivation."
            ),
            "linkedin": (
                "It is useful for professional positioning, "
                "partnerships, and business audiences."
            ),
            "tiktok": (
                "It can create broad awareness using concise, "
                "engaging short-form content."
            ),
            "x": (
                "It can support timely communication and "
                "public thought leadership."
            ),
        }

        return prefix + rationales.get(
            channel,
            "It provides an additional measurable marketing channel.",
        )

    @staticmethod
    def _content_types(
        channel: MarketingChannel,
    ) -> list[str]:
        content_map: dict[
            MarketingChannel,
            list[str],
        ] = {
            "google_business": [
                "Business updates",
                "Service highlights",
                "Customer reviews",
                "Frequently asked questions",
            ],
            "google_ads": [
                "Search advertisements",
                "Service landing pages",
                "Retargeting advertisements",
            ],
            "instagram": [
                "Educational posts",
                "Short videos",
                "Testimonials",
                "Behind-the-scenes content",
            ],
            "facebook": [
                "Community posts",
                "Customer stories",
                "Offers",
                "Educational content",
            ],
            "whatsapp": [
                "Lead follow-ups",
                "Appointment reminders",
                "Customer reactivation messages",
                "Promotional broadcasts",
            ],
            "email": [
                "Welcome sequence",
                "Educational campaign",
                "Promotional campaign",
                "Customer reactivation sequence",
            ],
            "linkedin": [
                "Professional insights",
                "Case studies",
                "Company updates",
                "Thought leadership",
            ],
            "tiktok": [
                "Short educational videos",
                "Quick tips",
                "Customer-focused stories",
            ],
            "x": [
                "Short insights",
                "Updates",
                "Industry commentary",
            ],
        }

        return content_map.get(
            channel,
            ["Educational content"],
        )

    @staticmethod
    def _posting_frequency(
        channel: MarketingChannel,
    ) -> str:
        frequencies: dict[
            MarketingChannel,
            str,
        ] = {
            "google_business": "2 updates per week",
            "google_ads": "Always-on with weekly optimization",
            "instagram": "3 to 4 posts per week",
            "facebook": "2 to 3 posts per week",
            "whatsapp": (
                "Follow up based on customer activity; "
                "maximum 1 promotional broadcast per week"
            ),
            "email": "1 campaign per week",
            "linkedin": "2 posts per week",
            "tiktok": "3 short videos per week",
            "x": "3 to 5 updates per week",
        }

        return frequencies.get(
            channel,
            "2 activities per week",
        )

    @staticmethod
    def _build_key_messages(
        business: MarketingBusinessProfile,
        analysis: MarketingBusinessAnalysis,
    ) -> list[str]:
        messages: list[str] = []

        differentiators = (
            MarketingStrategist._clean_values(
                business.differentiators
            )
        )

        if differentiators:
            for differentiator in differentiators[:3]:
                messages.append(
                    f"Choose {business.business_name} for "
                    f"{differentiator}."
                )

        messages.append(
            analysis.recommended_positioning
        )

        if business.products_or_services:
            services = MarketingStrategist._clean_values(
                business.products_or_services
            )

            if services:
                messages.append(
                    f"Access trusted support for "
                    f"{', '.join(services[:3])}."
                )

        return MarketingStrategist._deduplicate(
            messages
        )

    @staticmethod
    def _validate_budget_percentages(
        strategy: MarketingStrategy,
    ) -> None:
        if not strategy.channels:
            raise ValueError(
                "The marketing strategy must include at least "
                "one channel."
            )

        total = sum(
            channel.budget_percentage
            for channel in strategy.channels
        )

        if abs(total - 100) > 0.1:
            raise ValueError(
                "Marketing channel budget percentages must "
                "equal 100."
            )

    @staticmethod
    def _unique_channels(
        channels: list[MarketingChannel],
    ) -> list[MarketingChannel]:
        unique: list[MarketingChannel] = []

        for channel in channels:
            if channel not in unique:
                unique.append(channel)

        return unique

    @staticmethod
    def _clean_values(
        values: list[str],
    ) -> list[str]:
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

    @staticmethod
    def _deduplicate(
        values: list[str],
    ) -> list[str]:
        return MarketingStrategist._clean_values(
            values
        )


_marketing_strategist = MarketingStrategist()


def get_marketing_strategist() -> MarketingStrategist:
    """
    Return the shared Marketing Strategist instance.
    """

    return _marketing_strategist