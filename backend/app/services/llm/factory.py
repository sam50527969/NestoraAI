from __future__ import annotations

from app.services.llm.provider import (
    MockLLMProvider,
)


class LLMFactory:
    """
    Creates the configured LLM provider.
    """

    @staticmethod
    def create():
        return MockLLMProvider()


llm = LLMFactory.create()