from __future__ import annotations

from typing import Any, ClassVar

from sqlalchemy.orm import Session

from app.services.agents.agent_base import BaseAgent
from app.services.agents.crm_agent import CRMAgent
from app.services.agents.outreach_agent import OutreachAgent
from app.services.agents.research_agent import ResearchAgent
from app.services.agents.sales_agent import SalesAgent
from app.services.agents.website_agent import WebsiteAgent


class AgentRegistry:
    """
    Central registry for Nestora's AI workforce.

    The registry is responsible for:

    - registering available agent classes,
    - lazily creating agents for a mission,
    - retrieving agents by registry key,
    - discovering agents by capability,
    - exposing workforce metadata,
    - preventing disabled agents from being instantiated.

    Each MissionExecutor receives one AgentRegistry instance.
    """

    AGENT_CLASSES: ClassVar[dict[str, type[BaseAgent]]] = {
        "research": ResearchAgent,
        "crm": CRMAgent,
        "sales": SalesAgent,
        "website": WebsiteAgent,
        "outreach": OutreachAgent,
    }

    def __init__(
        self,
        db: Session,
        mission_id: str,
        request: Any,
    ) -> None:
        self.db = db
        self.mission_id = mission_id
        self.request = request

        self._agents: dict[str, BaseAgent] = {}

    # -------------------------------------------------
    # Registration
    # -------------------------------------------------

    @classmethod
    def normalize_key(cls, agent_key: str) -> str:
        """
        Normalize registry keys into a consistent format.

        Examples:

            "Research" -> "research"
            "website-agent" -> "website_agent"
        """

        return (
            str(agent_key)
            .strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )

    @classmethod
    def register(
        cls,
        agent_key: str,
        agent_class: type[BaseAgent],
        *,
        replace: bool = False,
    ) -> None:
        """
        Register an agent class globally.

        Future plugins may use this method to add new AI employees
        without editing the registry's internal implementation.
        """

        normalized_key = cls.normalize_key(agent_key)

        if not normalized_key:
            raise ValueError("Agent key cannot be empty.")

        if not issubclass(agent_class, BaseAgent):
            raise TypeError(
                "Registered agents must inherit from BaseAgent."
            )

        if (
            normalized_key in cls.AGENT_CLASSES
            and not replace
        ):
            raise KeyError(
                f"Agent key already registered: {normalized_key}"
            )

        cls.AGENT_CLASSES[normalized_key] = agent_class

    @classmethod
    def unregister(cls, agent_key: str) -> None:
        """
        Remove an agent class from the global registry.
        """

        normalized_key = cls.normalize_key(agent_key)

        if normalized_key not in cls.AGENT_CLASSES:
            raise KeyError(
                f"Unknown agent key: {normalized_key}"
            )

        del cls.AGENT_CLASSES[normalized_key]

    # -------------------------------------------------
    # Agent creation and retrieval
    # -------------------------------------------------

    def get(self, agent_key: str) -> BaseAgent:
        """
        Return one lazily created mission agent.

        The same instance is reused for the lifetime of this registry.
        """

        normalized_key = self.normalize_key(agent_key)

        agent_class = self.AGENT_CLASSES.get(normalized_key)

        if agent_class is None:
            available = ", ".join(
                sorted(self.AGENT_CLASSES.keys())
            )

            raise KeyError(
                f"Unknown agent key: {normalized_key}. "
                f"Available agents: {available}"
            )

        if not agent_class.ENABLED:
            raise RuntimeError(
                f"{agent_class.AGENT_NAME} is currently disabled."
            )

        if normalized_key not in self._agents:
            self._agents[normalized_key] = agent_class(
                db=self.db,
                mission_id=self.mission_id,
                request=self.request,
            )

        return self._agents[normalized_key]

    def research(self) -> ResearchAgent:
        return self.get("research")

    def crm(self) -> CRMAgent:
        return self.get("crm")

    def sales(self) -> SalesAgent:
        return self.get("sales")

    def website(self) -> WebsiteAgent:
        return self.get("website")

    def outreach(self) -> OutreachAgent:
        return self.get("outreach")

    # -------------------------------------------------
    # Workforce collections
    # -------------------------------------------------

    def all_agents(
        self,
        *,
        enabled_only: bool = True,
    ) -> dict[str, BaseAgent]:
        """
        Create and return the registered mission workforce.

        Disabled agents are skipped by default.
        """

        agents: dict[str, BaseAgent] = {}

        for agent_key, agent_class in self.AGENT_CLASSES.items():
            if enabled_only and not agent_class.ENABLED:
                continue

            agents[agent_key] = self.get(agent_key)

        return agents

    def created_agents(self) -> dict[str, BaseAgent]:
        """
        Return only agents already instantiated for this mission.
        """

        return dict(self._agents)

    @classmethod
    def registered_agent_classes(
        cls,
        *,
        enabled_only: bool = True,
    ) -> dict[str, type[BaseAgent]]:
        """
        Return registered agent classes without creating instances.
        """

        if not enabled_only:
            return dict(cls.AGENT_CLASSES)

        return {
            key: agent_class
            for key, agent_class in cls.AGENT_CLASSES.items()
            if agent_class.ENABLED
        }

    # -------------------------------------------------
    # Capability discovery
    # -------------------------------------------------

    @classmethod
    def find_classes_by_capability(
        cls,
        capability: str,
        *,
        enabled_only: bool = True,
    ) -> dict[str, type[BaseAgent]]:
        """
        Find registered agent classes supporting one capability.
        """

        matches: dict[str, type[BaseAgent]] = {}

        for agent_key, agent_class in cls.AGENT_CLASSES.items():
            if enabled_only and not agent_class.ENABLED:
                continue

            if agent_class.supports(capability):
                matches[agent_key] = agent_class

        return matches

    def find_by_capability(
        self,
        capability: str,
        *,
        enabled_only: bool = True,
    ) -> dict[str, BaseAgent]:
        """
        Return mission agent instances supporting one capability.
        """

        matches = self.find_classes_by_capability(
            capability,
            enabled_only=enabled_only,
        )

        return {
            agent_key: self.get(agent_key)
            for agent_key in matches
        }

    @classmethod
    def find_classes_supporting_any(
        cls,
        capabilities: list[str] | tuple[str, ...] | set[str],
        *,
        enabled_only: bool = True,
    ) -> dict[str, type[BaseAgent]]:
        """
        Find agent classes supporting at least one capability.
        """

        matches: dict[str, type[BaseAgent]] = {}

        for agent_key, agent_class in cls.AGENT_CLASSES.items():
            if enabled_only and not agent_class.ENABLED:
                continue

            if agent_class.supports_any(capabilities):
                matches[agent_key] = agent_class

        return matches

    @classmethod
    def find_classes_supporting_all(
        cls,
        capabilities: list[str] | tuple[str, ...] | set[str],
        *,
        enabled_only: bool = True,
    ) -> dict[str, type[BaseAgent]]:
        """
        Find agent classes supporting every requested capability.
        """

        matches: dict[str, type[BaseAgent]] = {}

        for agent_key, agent_class in cls.AGENT_CLASSES.items():
            if enabled_only and not agent_class.ENABLED:
                continue

            if agent_class.supports_all(capabilities):
                matches[agent_key] = agent_class

        return matches

    @classmethod
    def resolve_agent_key(
        cls,
        capability: str,
    ) -> str | None:
        """
        Resolve the first enabled agent capable of performing a task.

        This is an initial routing mechanism. A future scoring system
        may select between multiple matching agents using workload,
        confidence, cost, performance, or business preferences.
        """

        matches = cls.find_classes_by_capability(capability)

        if not matches:
            return None

        return next(iter(matches))

    def resolve_agent(
        self,
        capability: str,
    ) -> BaseAgent | None:
        """
        Return the first mission agent supporting a capability.
        """

        agent_key = self.resolve_agent_key(capability)

        if agent_key is None:
            return None

        return self.get(agent_key)

    # -------------------------------------------------
    # Metadata and inspection
    # -------------------------------------------------

    @classmethod
    def workforce_metadata(
        cls,
        *,
        enabled_only: bool = False,
    ) -> list[dict[str, Any]]:
        """
        Return metadata for the registered AI workforce.

        This can later power:

        - AI Workforce dashboard,
        - CEO Agent routing,
        - system health pages,
        - plugin discovery,
        - API endpoints.
        """

        workforce: list[dict[str, Any]] = []

        for agent_key, agent_class in cls.AGENT_CLASSES.items():
            if enabled_only and not agent_class.ENABLED:
                continue

            metadata = agent_class.metadata()
            metadata["key"] = agent_key

            workforce.append(metadata)

        return workforce

    @classmethod
    def available_capabilities(
        cls,
        *,
        enabled_only: bool = True,
    ) -> list[str]:
        """
        Return every unique capability offered by the workforce.
        """

        capabilities: set[str] = set()

        for agent_class in cls.registered_agent_classes(
            enabled_only=enabled_only,
        ).values():
            capabilities.update(
                agent_class.get_capabilities()
            )

        return sorted(capabilities)

    @classmethod
    def has_agent(cls, agent_key: str) -> bool:
        """
        Return whether an agent key is registered.
        """

        normalized_key = cls.normalize_key(agent_key)

        return normalized_key in cls.AGENT_CLASSES

    @classmethod
    def has_capability(cls, capability: str) -> bool:
        """
        Return whether any enabled agent supports a capability.
        """

        return bool(
            cls.find_classes_by_capability(capability)
        )