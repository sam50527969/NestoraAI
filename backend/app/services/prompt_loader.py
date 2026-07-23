from __future__ import annotations

from functools import lru_cache
from pathlib import Path


class PromptNotFoundError(FileNotFoundError):
    """Raised when a requested prompt file does not exist."""


class PromptLoader:
    """
    Loads Markdown prompt files from app/prompts.

    Prompt contents are cached after the first read to avoid
    repeated disk access during AI workflows.
    """

    def __init__(self) -> None:
        self._prompt_root = (
            Path(__file__)
            .resolve()
            .parent.parent
            / "prompts"
        )

    @lru_cache(maxsize=128)
    def load(self, relative_path: str) -> str:
        """
        Load one prompt file.

        Example:
            marketing/business_analysis.md
        """

        normalized_path = relative_path.strip().replace("\\", "/")

        prompt_path = (
            self._prompt_root / normalized_path
        ).resolve()

        try:
            prompt_path.relative_to(
                self._prompt_root.resolve()
            )
        except ValueError as exc:
            raise ValueError(
                "Prompt path must remain inside app/prompts."
            ) from exc

        if not prompt_path.is_file():
            raise PromptNotFoundError(
                f"Prompt not found: {normalized_path}"
            )

        content = prompt_path.read_text(
            encoding="utf-8"
        ).strip()

        if not content:
            raise ValueError(
                f"Prompt file is empty: {normalized_path}"
            )

        return content

    def exists(self, relative_path: str) -> bool:
        """
        Return whether a prompt file exists.
        """

        normalized_path = relative_path.strip().replace("\\", "/")

        prompt_path = (
            self._prompt_root / normalized_path
        ).resolve()

        try:
            prompt_path.relative_to(
                self._prompt_root.resolve()
            )
        except ValueError:
            return False

        return prompt_path.is_file()

    def available_prompts(self) -> list[str]:
        """
        Return every Markdown prompt path.
        """

        if not self._prompt_root.exists():
            return []

        return sorted(
            str(
                file.relative_to(
                    self._prompt_root
                )
            ).replace("\\", "/")
            for file in self._prompt_root.rglob("*.md")
            if file.is_file()
        )

    def clear_cache(self) -> None:
        """
        Clear cached prompt contents.

        Useful during development after editing prompt files
        without restarting the backend.
        """

        self.load.cache_clear()


_prompt_loader = PromptLoader()


def get_prompt_loader() -> PromptLoader:
    """
    Return the shared PromptLoader instance.
    """

    return _prompt_loader