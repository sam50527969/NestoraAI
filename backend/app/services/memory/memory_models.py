from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


# ---------------------------------------------------------
# Base Memory Entry
# ---------------------------------------------------------


@dataclass
class MemoryEntry:
    """
    Base class for every memory object stored by Nestora.

    Every memory item shares common metadata regardless of
    whether it represents a fact, observation, pattern,
    recommendation, or long-term business knowledge.
    """

    title: str
    content: str

    category: str = field(
        default="memory",
        init=False,
    )

    confidence: float = 1.0

    source: str = "System"

    tags: list[str] = field(
        default_factory=list,
    )

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    created_at: datetime = field(
        default_factory=datetime.utcnow,
    )

    updated_at: datetime = field(
        default_factory=datetime.utcnow,
    )

    last_confirmed: datetime | None = None

    active: bool = True

    def touch(self) -> None:
        """Update the modification timestamp."""
        self.updated_at = datetime.utcnow()

    def confirm(self) -> None:
        """Confirm this knowledge is still valid."""
        now = datetime.utcnow()
        self.last_confirmed = now
        self.updated_at = now

    def deactivate(self) -> None:
        """Mark a memory item as inactive."""
        self.active = False
        self.touch()


# ---------------------------------------------------------
# Facts
# ---------------------------------------------------------


@dataclass
class Fact(MemoryEntry):
    """
    A verified business fact.

    Example:
        Business opens at 8 AM.
        Marketing budget is 5000 QAR.
    """

    category: str = field(
        default="fact",
        init=False,
    )


# ---------------------------------------------------------
# Observations
# ---------------------------------------------------------


@dataclass
class Observation(MemoryEntry):
    """
    Something noticed by an AI agent.

    Example:
        Instagram generated more engagement than Facebook.
    """

    category: str = field(
        default="observation",
        init=False,
    )

    evidence: list[str] = field(
        default_factory=list,
    )


# ---------------------------------------------------------
# Patterns
# ---------------------------------------------------------


@dataclass
class Pattern(MemoryEntry):
    """
    A repeated observation.

    Example:
        Friday campaigns consistently outperform weekday campaigns.
    """

    category: str = field(
        default="pattern",
        init=False,
    )

    occurrences: int = 1


# ---------------------------------------------------------
# Recommendations
# ---------------------------------------------------------


@dataclass
class Recommendation(MemoryEntry):
    """
    Suggested action generated from previous learning.

    Example:
        Allocate 70% of the advertising budget to Instagram.
    """

    category: str = field(
        default="recommendation",
        init=False,
    )

    priority: int = 5


# ---------------------------------------------------------
# Business Knowledge
# ---------------------------------------------------------


@dataclass
class BusinessKnowledge(MemoryEntry):
    """
    High-value strategic knowledge.

    Example:
        This company grows primarily through referral marketing.
    """

    category: str = field(
        default="knowledge",
        init=False,
    )

    importance: int = 5


# ---------------------------------------------------------
# Memory Search Result
# ---------------------------------------------------------


@dataclass
class MemorySearchResult:
    """
    Result returned by the Memory Manager.

    This will later support semantic search and vector retrieval.
    """

    entry: MemoryEntry

    score: float = 1.0


# ---------------------------------------------------------
# Memory Statistics
# ---------------------------------------------------------


@dataclass
class MemoryStatistics:
    """
    Aggregate information about stored business memory.
    """

    total_entries: int = 0

    facts: int = 0

    observations: int = 0

    patterns: int = 0

    recommendations: int = 0

    knowledge: int = 0

    active_entries: int = 0

    inactive_entries: int = 0