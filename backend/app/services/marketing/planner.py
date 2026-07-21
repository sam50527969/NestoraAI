from __future__ import annotations

import json
import math
from collections.abc import Awaitable, Callable
from typing import Any

from app.schemas.marketing import (
    MarketingBusinessProfile,
    MarketingCampaignPlan,
    MarketingCampaignWeek,
    MarketingContentItem,
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


class MarketingPlannerError(RuntimeError):
    """Raised when a valid marketing campaign plan cannot be produced."""


class MarketingCampaignPlanner:
    """
    Builds a structured marketing campaign from an approved strategy.

    The planner supports two operating modes:

    1. AI mode when an LLM callable is supplied.
    2. Local fallback mode for development and testing.
    """

    PROMPT_PATH = "marketing/campaign_planner.md"

    def __init__(
        self,
        llm: LLMCallable | None = None,
        prompt_loader: PromptLoader | None = None,
    ) -> None:
        self._llm = llm
        self._prompt_loader = (
            prompt_loader or get_prompt_loader()
        )

    async def create_campaign(
        self,
        business: MarketingBusinessProfile,
        goal: MarketingGoal,
        strategy: MarketingStrategy,
        additional_instructions: str | None = None,
    ) -> MarketingCampaignPlan:
        """
        Create a structured campaign plan from the marketing strategy.
        """

        if self._llm is None:
            return self._build_fallback_campaign(
                business=business,
                goal=goal,
                strategy=strategy,
                additional_instructions=additional_instructions,
            )

        system_prompt = self._prompt_loader.load(
            self.PROMPT_PATH
        )

        user_prompt = self._build_user_prompt(
            business=business,
            goal=goal,
            strategy=strategy,
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

            campaign = MarketingCampaignPlan.model_validate(
                response_data
            )

            self._validate_campaign(
                campaign=campaign,
                goal=goal,
            )

            return campaign

        except Exception as exc:
            raise MarketingPlannerError(
                "Marketing Campaign Planner failed to produce "
                "a valid structured campaign."
            ) from exc

    def _build_user_prompt(
        self,
        business: MarketingBusinessProfile,
        goal: MarketingGoal,
        strategy: MarketingStrategy,
        additional_instructions: str | None,
    ) -> str:
        payload = {
            "business": business.model_dump(
                mode="json"
            ),
            "goal": goal.model_dump(
                mode="json"
            ),
            "strategy": strategy.model_dump(
                mode="json"
            ),
            "additional_instructions": (
                additional_instructions
            ),
        }

        return (
            "Create a practical week-by-week marketing campaign "
            "using the validated business profile, goal, and strategy.\n\n"
            "The campaign duration must match the goal timeline.\n"
            "Every week must contain a clear theme, objective, "
            "activities, and usable marketing content.\n\n"
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
                MarketingCampaignPlanner._remove_code_fence(
                    cleaned_response
                )
            )

        parsed = json.loads(cleaned_response)

        if not isinstance(parsed, dict):
            raise ValueError(
                "Marketing campaign response must be a JSON object."
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

    def _build_fallback_campaign(
        self,
        business: MarketingBusinessProfile,
        goal: MarketingGoal,
        strategy: MarketingStrategy,
        additional_instructions: str | None,
    ) -> MarketingCampaignPlan:
        total_weeks = max(
            1,
            math.ceil(goal.timeline_days / 7),
        )

        weeks: list[MarketingCampaignWeek] = []

        for week_number in range(
            1,
            total_weeks + 1,
        ):
            theme = self._week_theme(
                week_number=week_number,
                total_weeks=total_weeks,
            )

            objective = self._week_objective(
                week_number=week_number,
                total_weeks=total_weeks,
                goal=goal,
            )

            activities = self._build_week_activities(
                week_number=week_number,
                total_weeks=total_weeks,
                business=business,
                strategy=strategy,
                additional_instructions=additional_instructions,
            )

            content = self._build_week_content(
                week_number=week_number,
                business=business,
                strategy=strategy,
            )

            weeks.append(
                MarketingCampaignWeek(
                    week_number=week_number,
                    theme=theme,
                    objective=objective,
                    activities=activities,
                    content=content,
                )
            )

        status = (
            "pending_approval"
            if goal.approval_required
            else "draft"
        )

        return MarketingCampaignPlan(
            campaign_name=(
                f"{business.business_name} "
                f"{goal.timeline_days}-Day Marketing Campaign"
            ),
            duration_days=goal.timeline_days,
            campaign_objective=goal.objective,
            weeks=weeks,
            approval_required=goal.approval_required,
            status=status,
        )

    @staticmethod
    def _week_theme(
        week_number: int,
        total_weeks: int,
    ) -> str:
        if week_number == 1:
            return "Campaign Foundation and Setup"

        if week_number == 2:
            return "Awareness and Audience Education"

        if week_number == 3:
            return "Trust and Social Proof"

        if week_number == 4:
            return "Lead Generation and Enquiry Growth"

        if week_number == total_weeks:
            return "Conversion, Review, and Optimization"

        cycle = (
            week_number - 5
        ) % 4

        themes = [
            "Audience Engagement",
            "Customer Follow-up",
            "Offer and Service Promotion",
            "Performance Optimization",
        ]

        return themes[cycle]

    @staticmethod
    def _week_objective(
        week_number: int,
        total_weeks: int,
        goal: MarketingGoal,
    ) -> str:
        if week_number == 1:
            return (
                "Prepare campaign assets, tracking, channel setup, "
                "and approval workflows."
            )

        if week_number == 2:
            return (
                "Increase awareness and educate the target audience "
                "about the business's main services."
            )

        if week_number == 3:
            return (
                "Build customer trust using proof, reviews, "
                "expertise, and useful information."
            )

        if week_number == 4:
            return (
                "Generate qualified enquiries through clear offers "
                "and direct calls to action."
            )

        if week_number == total_weeks:
            return (
                "Maximize conversions, review campaign performance, "
                f"and measure progress toward: {goal.objective}"
            )

        return (
            "Maintain campaign momentum, generate enquiries, "
            "and improve results using performance data."
        )

    def _build_week_activities(
        self,
        week_number: int,
        total_weeks: int,
        business: MarketingBusinessProfile,
        strategy: MarketingStrategy,
        additional_instructions: str | None,
    ) -> list[str]:
        activities: list[str] = []

        if week_number == 1:
            activities.extend(
                [
                    "Confirm campaign goals, budget, and approval process.",
                    "Review and update business profiles on selected channels.",
                    "Prepare campaign tracking for enquiries, leads, and conversions.",
                    "Create a shared campaign calendar and assign responsibilities.",
                ]
            )

        elif week_number == 2:
            activities.extend(
                [
                    "Publish educational content introducing key services.",
                    "Create audience-focused frequently asked questions.",
                    "Promote the business's main differentiators.",
                    "Begin monitoring engagement and enquiry sources.",
                ]
            )

        elif week_number == 3:
            activities.extend(
                [
                    "Publish customer testimonials or approved success stories.",
                    "Request reviews from satisfied existing customers.",
                    "Share expert advice that addresses common customer concerns.",
                    "Respond to comments, messages, and enquiries promptly.",
                ]
            )

        elif week_number == 4:
            activities.extend(
                [
                    "Launch a focused lead-generation offer or campaign.",
                    "Use clear booking or enquiry calls to action.",
                    "Follow up with new leads within the agreed response time.",
                    "Review lead quality by channel.",
                ]
            )

        elif week_number == total_weeks:
            activities.extend(
                [
                    "Follow up with all qualified but unconverted leads.",
                    "Compare channel performance against campaign targets.",
                    "Identify the strongest messages and content types.",
                    "Prepare recommendations for the next campaign cycle.",
                ]
            )

        else:
            activities.extend(
                [
                    "Publish planned campaign content across priority channels.",
                    "Follow up with new and existing prospects.",
                    "Review weekly engagement, leads, and conversion indicators.",
                    "Adjust messages and activities based on performance.",
                ]
            )

        channel_activities = self._channel_activities(
            strategy=strategy,
            week_number=week_number,
        )

        activities.extend(channel_activities)

        if additional_instructions:
            activities.append(
                "Apply the supplied additional campaign instructions: "
                f"{additional_instructions.strip()}"
            )

        return self._deduplicate(
            activities
        )

    def _channel_activities(
        self,
        strategy: MarketingStrategy,
        week_number: int,
    ) -> list[str]:
        activities: list[str] = []

        for channel_strategy in strategy.channels:
            channel = channel_strategy.channel

            if channel == "google_business":
                activities.append(
                    "Publish a Google Business update and review "
                    "business information for accuracy."
                )

            elif channel == "google_ads":
                activities.append(
                    "Review Google Ads search terms, lead quality, "
                    "and campaign budget allocation."
                )

            elif channel == "instagram":
                activities.append(
                    "Publish Instagram educational, trust-building, "
                    "or promotional content."
                )

            elif channel == "facebook":
                activities.append(
                    "Publish a Facebook post targeted to the local audience."
                )

            elif channel == "whatsapp":
                activities.append(
                    "Send approved WhatsApp follow-ups to relevant "
                    "leads or existing customers."
                )

            elif channel == "email":
                activities.append(
                    "Send one approved email campaign or nurture message."
                )

            elif channel == "linkedin":
                activities.append(
                    "Publish a professional LinkedIn insight or business update."
                )

            elif channel == "tiktok":
                activities.append(
                    "Publish a short educational or customer-focused video."
                )

            elif channel == "x":
                activities.append(
                    "Publish timely short updates and respond to engagement."
                )

        if week_number > 1:
            activities.append(
                "Compare this week's channel results with the previous week."
            )

        return activities

    def _build_week_content(
        self,
        week_number: int,
        business: MarketingBusinessProfile,
        strategy: MarketingStrategy,
    ) -> list[MarketingContentItem]:
        content_items: list[MarketingContentItem] = []

        for channel_strategy in strategy.channels:
            channel = channel_strategy.channel

            content_items.append(
                MarketingContentItem(
                    channel=channel,
                    title=self._content_title(
                        week_number=week_number,
                        business=business,
                        channel=channel,
                    ),
                    content=self._content_body(
                        week_number=week_number,
                        business=business,
                        strategy=strategy,
                        channel=channel,
                    ),
                    call_to_action=self._call_to_action(
                        channel=channel
                    ),
                    suggested_publish_time=(
                        self._suggested_publish_time(
                            channel=channel
                        )
                    ),
                    hashtags=self._hashtags(
                        business=business,
                        channel=channel,
                    ),
                )
            )

        return content_items

    @staticmethod
    def _content_title(
        week_number: int,
        business: MarketingBusinessProfile,
        channel: str,
    ) -> str:
        titles = {
            1: f"Welcome to {business.business_name}",
            2: "What Customers Should Know Before Choosing a Service",
            3: "Why Customers Trust Our Team",
            4: "Take the Next Step Today",
        }

        default_title = (
            f"{business.business_name} Weekly Update"
        )

        title = titles.get(
            week_number,
            default_title,
        )

        return f"{title} — {channel.replace('_', ' ').title()}"

    @staticmethod
    def _content_body(
        week_number: int,
        business: MarketingBusinessProfile,
        strategy: MarketingStrategy,
        channel: str,
    ) -> str:
        service_text = (
            ", ".join(
                business.products_or_services[:3]
            )
            if business.products_or_services
            else "our services"
        )

        key_message = (
            strategy.key_messages[0]
            if strategy.key_messages
            else strategy.primary_objective
        )

        if week_number == 1:
            return (
                f"Discover how {business.business_name} supports "
                f"customers with {service_text}. {key_message}"
            )

        if week_number == 2:
            return (
                f"Choosing the right provider matters. "
                f"{business.business_name} offers {service_text} "
                f"with a clear focus on customer needs."
            )

        if week_number == 3:
            return (
                f"Trust is built through consistent service, clear "
                f"communication, and reliable support. "
                f"{business.business_name} is ready to help."
            )

        if week_number == 4:
            return (
                f"Looking for {service_text}? Contact "
                f"{business.business_name} today to learn more "
                f"or make an enquiry."
            )

        return (
            f"This week's {channel.replace('_', ' ')} update from "
            f"{business.business_name}: {key_message}"
        )

    @staticmethod
    def _call_to_action(
        channel: str,
    ) -> str:
        calls_to_action = {
            "google_business": (
                "Call or request directions to visit us."
            ),
            "google_ads": (
                "Click to learn more or submit an enquiry."
            ),
            "instagram": (
                "Send us a direct message to learn more."
            ),
            "facebook": (
                "Message us today for more information."
            ),
            "whatsapp": (
                "Reply to this message to ask a question "
                "or request an appointment."
            ),
            "email": (
                "Reply to this email or contact us to get started."
            ),
            "linkedin": (
                "Contact our team to discuss how we can help."
            ),
            "tiktok": (
                "Follow us and message us for more information."
            ),
            "x": (
                "Send us a message to learn more."
            ),
        }

        return calls_to_action.get(
            channel,
            "Contact us today to learn more.",
        )

    @staticmethod
    def _suggested_publish_time(
        channel: str,
    ) -> str:
        publish_times = {
            "google_business": "Tuesday at 10:00",
            "google_ads": "Always active with weekly review",
            "instagram": "Tuesday or Thursday at 19:00",
            "facebook": "Wednesday at 18:00",
            "whatsapp": "Sunday to Thursday between 10:00 and 17:00",
            "email": "Tuesday at 10:00",
            "linkedin": "Tuesday at 09:00",
            "tiktok": "Thursday at 19:00",
            "x": "Weekday morning between 09:00 and 11:00",
        }

        return publish_times.get(
            channel,
            "Weekday during business hours",
        )

    @staticmethod
    def _hashtags(
        business: MarketingBusinessProfile,
        channel: str,
    ) -> list[str]:
        if channel in {
            "whatsapp",
            "email",
            "google_ads",
        }:
            return []

        values = [
            business.business_name,
            business.industry,
        ]

        if business.location:
            values.append(
                business.location
            )

        hashtags: list[str] = []

        for value in values:
            normalized = "".join(
                character
                for character in value.title()
                if character.isalnum()
            )

            if normalized:
                hashtags.append(
                    f"#{normalized}"
                )

        return MarketingCampaignPlanner._deduplicate(
            hashtags
        )

    @staticmethod
    def _validate_campaign(
        campaign: MarketingCampaignPlan,
        goal: MarketingGoal,
    ) -> None:
        if campaign.duration_days != goal.timeline_days:
            raise ValueError(
                "Campaign duration must match the marketing "
                "goal timeline."
            )

        if not campaign.weeks:
            raise ValueError(
                "Campaign must contain at least one week."
            )

        expected_weeks = max(
            1,
            math.ceil(goal.timeline_days / 7),
        )

        if len(campaign.weeks) != expected_weeks:
            raise ValueError(
                "Campaign week count does not match the "
                "goal timeline."
            )

        week_numbers = [
            week.week_number
            for week in campaign.weeks
        ]

        expected_numbers = list(
            range(
                1,
                expected_weeks + 1,
            )
        )

        if week_numbers != expected_numbers:
            raise ValueError(
                "Campaign week numbers must be sequential."
            )

        for week in campaign.weeks:
            if not week.activities:
                raise ValueError(
                    f"Campaign week {week.week_number} "
                    "must contain at least one activity."
                )

    @staticmethod
    def _deduplicate(
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
            cleaned.append(
                normalized
            )

        return cleaned


_marketing_campaign_planner = MarketingCampaignPlanner()


def get_marketing_campaign_planner() -> MarketingCampaignPlanner:
    """
    Return the shared Marketing Campaign Planner instance.
    """

    return _marketing_campaign_planner