from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from app.services.memory.memory_models import (
    BusinessKnowledge,
    Fact,
    MemoryEntry,
    MemorySearchResult,
    MemoryStatistics,
    Observation,
    Pattern,
    Recommendation,
)


class MemoryManager:
    """
    Central business memory service.

    Every AI agent interacts with business memory exclusively
    through this class.

    Storage is intentionally abstract. Today's implementation
    uses an in-memory store. Future versions can replace it
    with SQLite, PostgreSQL, Redis, or a vector database
    without changing agent code.
    """

    def __init__(self):
        # business_id -> MemoryEntry[]
        self._memory: dict[str, list[MemoryEntry]] = defaultdict(list)

    # ---------------------------------------------------------
    # Core Operations
    # ---------------------------------------------------------

    def remember(
        self,
        business_id: str,
        entry: MemoryEntry,
    ) -> MemoryEntry:
        """
        Store a new memory item.
        """

        self._memory[business_id].append(entry)
        return entry

    def recall(
        self,
        business_id: str,
    ) -> list[MemoryEntry]:
        """
        Return all active memory for a business.
        """

        return [
            entry
            for entry in self._memory.get(business_id, [])
            if entry.active
        ]

    def forget(
        self,
        business_id: str,
        title: str,
    ) -> bool:
        """
        Soft-delete memory by title.
        """

        for entry in self._memory.get(business_id, []):
            if entry.title == title:
                entry.deactivate()
                return True

        return False

    # ---------------------------------------------------------
    # Search
    # ---------------------------------------------------------

    def search(
        self,
        business_id: str,
        *,
        text: str | None = None,
        category: str | None = None,
        tags: Iterable[str] | None = None,
    ) -> list[MemorySearchResult]:
        """
        Search business memory.
        """

        results: list[MemorySearchResult] = []

        tag_set = {
            tag.lower()
            for tag in (tags or [])
        }

        for entry in self.recall(business_id):

            if category and entry.category != category:
                continue

            if text:
                haystack = (
                    entry.title
                    + " "
                    + entry.content
                ).lower()

                if text.lower() not in haystack:
                    continue

            if tag_set:

                entry_tags = {
                    t.lower()
                    for t in entry.tags
                }

                if not tag_set.intersection(entry_tags):
                    continue

            results.append(
                MemorySearchResult(
                    entry=entry,
                    score=entry.confidence,
                )
            )

        results.sort(
            key=lambda r: r.score,
            reverse=True,
        )

        return results

    # ---------------------------------------------------------
    # Learning
    # ---------------------------------------------------------

    def learn(
        self,
        business_id: str,
        observation: str,
        *,
        confidence: float = 0.75,
        source: str = "AI",
        tags: list[str] | None = None,
    ) -> Observation:
        """
        Convenience helper for recording observations.
        """

        entry = Observation(
            title="Observation",
            content=observation,
            confidence=confidence,
            source=source,
            tags=tags or [],
        )

        self.remember(
            business_id,
            entry,
        )

        return entry

    # ---------------------------------------------------------
    # Recommendations
    # ---------------------------------------------------------

    def recommend(
        self,
        business_id: str,
        topic: str | None = None,
    ) -> list[Recommendation]:
        """
        Return stored recommendations.

        Future versions will generate AI recommendations.
        """

        recommendations = []

        for entry in self.recall(business_id):

            if not isinstance(
                entry,
                Recommendation,
            ):
                continue

            if topic:

                haystack = (
                    entry.title
                    + " "
                    + entry.content
                ).lower()

                if topic.lower() not in haystack:
                    continue

            recommendations.append(entry)

        recommendations.sort(
            key=lambda r: (
                r.priority,
                r.confidence,
            ),
            reverse=True,
        )

        return recommendations

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    def statistics(
        self,
        business_id: str,
    ) -> MemoryStatistics:
        """
        Return aggregate memory statistics.
        """

        stats = MemoryStatistics()

        entries = self._memory.get(
            business_id,
            [],
        )

        stats.total_entries = len(entries)

        for entry in entries:

            if entry.active:
                stats.active_entries += 1
            else:
                stats.inactive_entries += 1

            if isinstance(entry, Fact):
                stats.facts += 1

            elif isinstance(entry, Observation):
                stats.observations += 1

            elif isinstance(entry, Pattern):
                stats.patterns += 1

            elif isinstance(entry, Recommendation):
                stats.recommendations += 1

            elif isinstance(entry, BusinessKnowledge):
                stats.knowledge += 1

        return stats

    # ---------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------

    def clear_business(
        self,
        business_id: str,
    ) -> None:
        """
        Remove all memory for one business.
        """

        self._memory.pop(
            business_id,
            None,
        )

    def businesses(self) -> list[str]:
        """
        Return all businesses currently stored.
        """

        return sorted(
            self._memory.keys()
        )

    def has_business(
        self,
        business_id: str,
    ) -> bool:
        return business_id in self._memory