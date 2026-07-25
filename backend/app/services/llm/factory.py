from __future__ import annotations

import os

from app.services.llm.gemini import GeminiLLMProvider
from app.services.llm.provider import MockLLMProvider


class LLMFactory:
    """
    Creates the LLM provider selected through the LLM_PROVIDER
    environment variable.
    """

    @staticmethod
    def create():
        provider_name = os.getenv(
            "LLM_PROVIDER",
            "mock",
        ).strip().lower()

        if provider_name == "mock":
            return MockLLMProvider()

        if provider_name == "gemini":
            return GeminiLLMProvider()

        raise ValueError(
            f"Unsupported LLM provider: '{provider_name}'. "
            "Currently supported providers are: mock and gemini."
        )


llm = LLMFactory.create()