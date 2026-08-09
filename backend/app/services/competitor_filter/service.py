from __future__ import annotations

import re
from typing import Any

from app.services.competitor_filter.industry_rules import (
    get_industry_rules,
    normalize_industry,
)
from app.services.competitor_filter.models import (
    CompetitorRelevanceBreakdown,
    CompetitorRelevanceResult,
)


def _normalize_text(value: Any) -> str:
    """
    Normalize text for reliable category and keyword matching.
    """
    return " ".join(
        str(value or "")
        .strip()
        .lower()
        .replace("_", " ")
        .replace("-", " ")
        .split()
    )


def _contains_term(
    text: str,
    term: str,
) -> bool:
    """
    Match a term as a word/phrase instead of using a loose
    substring search. This helps avoid accidental matches.
    """
    normalized_text = _normalize_text(text)
    normalized_term = _normalize_text(term)

    if not normalized_term:
        return False

    pattern = (
        r"(?<!\w)"
        + re.escape(normalized_term)
        + r"(?!\w)"
    )

    return bool(
        re.search(
            pattern,
            normalized_text,
            flags=re.IGNORECASE,
        )
    )


def _location_matches(
    business_location: str,
    target_location: str | None,
) -> bool:
    """
    Use the main location token rather than requiring the
    entire target string to appear exactly.

    Example:
        target_location = "Doha, Qatar"
        business_location = "... الدوحة, قطر"

    This function intentionally treats location as a small
    supporting signal only.
    """
    if not target_location:
        return False

    target = _normalize_text(
        str(target_location)
        .replace(",", " ")
    )

    business = _normalize_text(
        str(business_location)
        .replace(",", " ")
    )

    if not target or not business:
        return False

    target_tokens = [
        token
        for token in target.split()
        if len(token) >= 3
    ]

    return any(
        token in business
        for token in target_tokens
    )


class CompetitorFilterService:
    """
    Score and filter candidate competitors according to
    relevance to the requested industry.

    The filter uses category, business-name keywords,
    industry aliases, exclusion rules, and location.

    Category evidence is treated as stronger than a generic
    keyword match, while explicit conflicting categories
    remain hard exclusions.
    """

    def evaluate(
        self,
        *,
        competitor: dict[str, Any],
        target_industry: str,
        target_location: str | None = None,
    ) -> CompetitorRelevanceResult:
        rules = get_industry_rules(
            target_industry
        )

        normalized_industry = _normalize_text(
            normalize_industry(
                target_industry
            )
        )

        business_name = str(
            competitor.get("businessName")
            or competitor.get("business_name")
            or competitor.get("name")
            or "Unknown business"
        ).strip()

        category = _normalize_text(
            competitor.get("category")
            or competitor.get("industry")
        )

        location = _normalize_text(
            competitor.get("location")
            or competitor.get("address")
        )

        description = _normalize_text(
            competitor.get("description")
        )

        name_text = _normalize_text(
            business_name
        )

        combined_text = _normalize_text(
            " ".join(
                [
                    business_name,
                    category,
                    description,
                ]
            )
        )

        breakdown = (
            CompetitorRelevanceBreakdown()
        )

        matched_terms: list[str] = []
        excluded_terms: list[str] = []

        allowed_categories = {
            _normalize_text(value)
            for value in rules.get(
                "allowed_categories",
                []
            )
            if _normalize_text(value)
        }

        excluded_categories = {
            _normalize_text(value)
            for value in rules.get(
                "excluded_categories",
                []
            )
            if _normalize_text(value)
        }

        positive_terms = [
            _normalize_text(value)
            for value in rules.get(
                "positive_terms",
                []
            )
            if _normalize_text(value)
        ]

        exclusion_terms = [
            _normalize_text(value)
            for value in rules.get(
                "excluded_terms",
                []
            )
            if _normalize_text(value)
        ]

        aliases = [
            _normalize_text(value)
            for value in rules.get(
                "aliases",
                []
            )
            if _normalize_text(value)
        ]

        # -------------------------------------------------
        # 1. Industry / alias signal
        # -------------------------------------------------
        if (
            normalized_industry
            and _contains_term(
                combined_text,
                normalized_industry,
            )
        ):
            breakdown.industry_match = 30

        elif any(
            _contains_term(
                combined_text,
                alias,
            )
            for alias in aliases
        ):
            breakdown.industry_match = 22

        # -------------------------------------------------
        # 2. Category signal
        # -------------------------------------------------
        exact_category_match = bool(
            category
            and category in allowed_categories
        )

        related_category_match = bool(
            category
            and any(
                allowed
                and (
                    allowed in category
                    or category in allowed
                )
                for allowed in allowed_categories
            )
        )

        if exact_category_match:
            breakdown.category_match = 40

        elif related_category_match:
            breakdown.category_match = 30

        # -------------------------------------------------
        # 3. Positive keyword signal
        # -------------------------------------------------
        for term in positive_terms:
            if _contains_term(
                combined_text,
                term,
            ):
                matched_terms.append(
                    term
                )

        matched_terms = list(
            dict.fromkeys(
                matched_terms
            )
        )

        if len(matched_terms) >= 3:
            breakdown.keyword_match = 25

        elif len(matched_terms) == 2:
            breakdown.keyword_match = 18

        elif len(matched_terms) == 1:
            breakdown.keyword_match = 10

        # -------------------------------------------------
        # 4. Location signal
        # -------------------------------------------------
        if _location_matches(
            location,
            target_location,
        ):
            breakdown.location_match = 5

        # -------------------------------------------------
        # 5. Exclusions
        # -------------------------------------------------
        category_conflict = bool(
            category
            and category in excluded_categories
        )

        if category_conflict:
            breakdown.exclusion_penalty += 100
            excluded_terms.append(
                category
            )

        # Only use exclusion words from name/category/description,
        # not the address. This avoids accidental geographic text
        # causing exclusions.
        for term in exclusion_terms:
            if _contains_term(
                combined_text,
                term,
            ):
                excluded_terms.append(
                    term
                )

        excluded_terms = list(
            dict.fromkeys(
                excluded_terms
            )
        )

        # If the category itself is valid, a generic exclusion term
        # found in the name should not automatically reject it.
        # Example: a legitimate "Pet Medical Center" would still be
        # rejected for a normal medical-center search only if its
        # category or clear business identity conflicts.
        semantic_conflict = bool(
            excluded_terms
            and not exact_category_match
            and not related_category_match
        )

        if semantic_conflict:
            breakdown.exclusion_penalty += 60

        has_hard_exclusion = bool(
            category_conflict
            or semantic_conflict
        )

        # -------------------------------------------------
        # 6. Final score
        # -------------------------------------------------
        raw_score = (
            breakdown.industry_match
            + breakdown.category_match
            + breakdown.keyword_match
            + breakdown.location_match
            - breakdown.exclusion_penalty
        )

        score = max(
            0,
            min(
                100,
                raw_score,
            ),
        )

        # Category evidence is strong enough on its own.
        has_relevant_category = (
            breakdown.category_match >= 30
        )

        has_relevant_language = bool(
            breakdown.industry_match >= 20
            or breakdown.keyword_match >= 10
        )

        included = bool(
            not has_hard_exclusion
            and (
                score >= 35
                or has_relevant_category
                or (
                    has_relevant_language
                    and score >= 25
                )
            )
        )

        # -------------------------------------------------
        # 7. Explanation
        # -------------------------------------------------
        if has_hard_exclusion:
            reason = (
                "Excluded because the business category "
                "or identity conflicts with the target "
                "industry."
            )

        elif (
            breakdown.category_match >= 40
            and score >= 70
        ):
            reason = (
                "Strong category and industry match."
            )

        elif breakdown.category_match >= 30:
            reason = (
                "Relevant business category for the "
                "target competitive market."
            )

        elif score >= 50:
            reason = (
                "Good keyword and industry relevance."
            )

        elif included:
            reason = (
                "Potentially relevant competitor based "
                "on available public business data."
            )

        else:
            reason = (
                "Insufficient evidence that this business "
                "belongs to the target competitive market."
            )

        # -------------------------------------------------
        # 8. Confidence
        # -------------------------------------------------
        confidence = 35

        if breakdown.category_match >= 40:
            confidence += 35
        elif breakdown.category_match >= 30:
            confidence += 25

        if breakdown.industry_match > 0:
            confidence += 15

        if breakdown.keyword_match > 0:
            confidence += 10

        if has_hard_exclusion:
            confidence = max(
                confidence,
                90,
            )

        confidence = min(
            100,
            confidence,
        )

        return CompetitorRelevanceResult(
            business_name=business_name,
            score=score,
            included=included,
            reason=reason,
            breakdown=breakdown,
            matched_terms=matched_terms,
            excluded_terms=excluded_terms,
            confidence=confidence,
        )

    def filter_competitors(
        self,
        *,
        competitors: list[
            dict[str, Any]
        ],
        target_industry: str,
        target_location: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        evaluated: list[
            dict[str, Any]
        ] = []

        for competitor in competitors:
            relevance = self.evaluate(
                competitor=competitor,
                target_industry=target_industry,
                target_location=target_location,
            )

            # Useful during development and safe to keep.
            print(
                "[CompetitorFilter] "
                f"{relevance.business_name} | "
                f"score={relevance.score} | "
                f"included={relevance.included} | "
                f"matched={relevance.matched_terms} | "
                f"excluded={relevance.excluded_terms}"
            )

            if not relevance.included:
                continue

            enriched = dict(
                competitor
            )

            enriched[
                "competitor_relevance"
            ] = relevance.to_dict()

            enriched[
                "relevanceScore"
            ] = relevance.score

            enriched[
                "relevanceConfidence"
            ] = relevance.confidence

            evaluated.append(
                enriched
            )

        evaluated.sort(
            key=lambda competitor: (
                competitor.get(
                    "relevanceScore",
                    0,
                ),
                competitor.get(
                    "relevanceConfidence",
                    0,
                ),
            ),
            reverse=True,
        )

        if limit is not None:
            safe_limit = max(
                0,
                int(limit),
            )

            return evaluated[
                :safe_limit
            ]

        return evaluated