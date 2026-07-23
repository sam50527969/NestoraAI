from __future__ import annotations

from app.services.llm.base import BaseLLMProvider


class MockLLMProvider(BaseLLMProvider):
    """
    Temporary provider used while the architecture
    is being built.
    """

    async def generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> str:

        return (
            "MOCK RESPONSE\n\n"
            f"System:\n{system_prompt}\n\n"
            f"User:\n{user_prompt}"
        )